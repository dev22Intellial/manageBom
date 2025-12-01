from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Import messages
from .forms import BOMUploadForm
from .models import BOMFile, BOMEntry, Part
from django.http import JsonResponse
import openpyxl
import io
import tempfile
import os
from .parser_factory import get_bom_parser # Import the factory

@login_required
def home(request):
    master_boms = BOMFile.objects.filter(user=request.user, is_master=True).order_by('-uploaded_at')
    context = {
        'master_boms': master_boms
    }
    return render(request, 'home.html', context)

@login_required
def upload_master_bom(request):
    if request.method == 'POST':
        form = BOMUploadForm(request.POST, request.FILES)
        if form.is_valid():
            bom_file = form.save(commit=False)
            bom_file.user = request.user
            bom_file.is_master = True
            bom_file.save()
            return redirect('home')
    else:
        form = BOMUploadForm()
    return render(request, 'upload_bom.html', {'form': form})

def parse_xlsx_and_save(bom_file_instance):
    """
    Parses an XLSX file, finds the required columns, and populates the database.
    Returns a tuple (success_boolean, error_message_string).
    """
    try:
        workbook = openpyxl.load_workbook(bom_file_instance.file.path)
        sheet = workbook.active

        # Find header columns
        headers = [cell.value for cell in sheet[1]]
        required_columns = ['Reference designators', 'Quantity', 'Identified MPN', 'Identified manufacturer']
        missing_columns = [col for col in required_columns if col not in headers]

        if missing_columns:
            return (False, f"The file is missing the following required columns: {', '.join(missing_columns)}.")

        column_map = {col: headers.index(col) for col in required_columns}

        # Parse rows
        for row_index in range(2, sheet.max_row + 1):
            row_data = [cell.value for cell in sheet[row_index]]
            
            if not any(row_data):
                continue

            mpn = row_data[column_map['Identified MPN']]
            manufacturer = row_data[column_map['Identified manufacturer']]
            
            if not mpn or not manufacturer:
                continue

            part, _ = Part.objects.get_or_create(
                mpn=mpn,
                manufacturer=manufacturer
            )
            
            BOMEntry.objects.create(
                bom_file=bom_file_instance,
                part=part,
                quantity=int(row_data[column_map['Quantity']]),
                reference_designators=row_data[column_map['Reference designators']]
            )
        return (True, None)
    except Exception as e:
        return (False, f"An unexpected error occurred while parsing the file: {e}")


@login_required
def get_bom_data(request, bom_file_id):
    bom_file = get_object_or_404(BOMFile, pk=bom_file_id, user=request.user)
    
    if not BOMEntry.objects.filter(bom_file=bom_file).exists():
        success, error_message = parse_xlsx_and_save(bom_file)
        if not success:
            return JsonResponse({'error': error_message}, status=500)

    entries = BOMEntry.objects.filter(bom_file=bom_file)
    data = {
        'file_name': bom_file.name,
        'entries': [
            {
                'mpn': entry.part.mpn,
                'manufacturer': entry.part.manufacturer,
                'quantity': entry.quantity,
                'designators': entry.reference_designators,
            }
            for entry in entries
        ]
    }
    return JsonResponse(data)

def _perform_comparison(master_bom_entries, target_bom_entries):
    """
    Compares two BOMs and returns categorized differences along with summary counts.
    """
    master_parts_map = {}
    for entry in master_bom_entries:
        key = (entry['mpn'], entry['manufacturer'])
        master_parts_map[key] = {
            'quantity': entry['quantity'],
            'designators': entry['designators']
        }
    
    target_parts_map = {}
    for entry in target_bom_entries:
        key = (entry['mpn'], entry['manufacturer'])
        target_parts_map[key] = {
            'quantity': entry['quantity'],
            'designators': entry['designators']
        }

    matching_parts = []
    added_parts = []
    removed_parts = []

    perfectly_matching_count = 0
    partially_matching_count = 0
    totally_different_count = 0 # This will be sum of added_parts + removed_parts

    # Check for matching and removed parts
    for master_key, master_data in master_parts_map.items():
        if master_key in target_parts_map:
            target_data = target_parts_map[master_key]
            if (master_data['quantity'] != target_data['quantity']) or \
               (master_data['designators'] != target_data['designators']):
                partially_matching_count += 1
                matching_parts.append({
                    'mpn': master_key[0],
                    'manufacturer': master_key[1],
                    'master_quantity': master_data['quantity'],
                    'target_quantity': target_data['quantity'],
                    'master_designators': master_data['designators'],
                    'target_designators': target_data['designators'],
                    'status': 'Quantity/Designator Changed'
                })
            else:
                perfectly_matching_count += 1
                matching_parts.append({
                    'mpn': master_key[0],
                    'manufacturer': master_key[1],
                    'quantity': master_data['quantity'],
                    'designators': master_data['designators'],
                    'status': 'Identical'
                })
        else:
            totally_different_count += 1 # Part removed from master
            removed_parts.append({
                'mpn': master_key[0],
                'manufacturer': master_key[1],
                'quantity': master_data['quantity'],
                'designators': master_data['designators'],
            })
    
    # Check for added parts
    for target_key, target_data in target_parts_map.items():
        if target_key not in master_parts_map:
            totally_different_count += 1 # Part added to target
            added_parts.append({
                'mpn': target_key[0],
                'manufacturer': target_key[1],
                'quantity': target_data['quantity'],
                'designators': target_data['designators'],
            })
    
    return {
        'matching_parts': matching_parts,
        'added_parts': added_parts,
        'removed_parts': removed_parts,
        'summary': {
            'perfectly_matching': perfectly_matching_count,
            'partially_matching': partially_matching_count,
            'totally_different': totally_different_count,
        }
    }


@login_required
def compare_boms(request, master_bom_id):
    if request.method == 'POST':
        master_bom = get_object_or_404(BOMFile, pk=master_bom_id, user=request.user, is_master=True)
        
        target_files = request.FILES.getlist('target_files')
        
        if not target_files:
            messages.error(request, "No target files were uploaded for comparison.")
            return redirect('home')

        # Ensure master BOM is parsed
        if not BOMEntry.objects.filter(bom_file=master_bom).exists():
            success, error_message = parse_xlsx_and_save(master_bom)
            if not success:
                messages.error(request, f"Error parsing Master BOM '{master_bom.name}': {error_message}")
                return redirect('home')
        
        master_bom_entries = []
        for entry in BOMEntry.objects.filter(bom_file=master_bom):
            master_bom_entries.append({
                'mpn': entry.part.mpn,
                'manufacturer': entry.part.manufacturer,
                'quantity': entry.quantity,
                'designators': entry.reference_designators,
            })

        all_comparison_results = []
        global_parsing_errors = []

        for uploaded_file in target_files:
            # Create a temporary file with the original extension
            file_extension = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            try:
                parser = get_bom_parser(temp_file_path, uploaded_file.name) 
                target_parsed_data = parser.parse(temp_file_path)
                
                if not target_parsed_data:
                    global_parsing_errors.append(f"No valid BOM entries found in '{uploaded_file.name}'.")
                    continue

                comparison_result = _perform_comparison(master_bom_entries, target_parsed_data)
                all_comparison_results.append({
                    'target_file_name': uploaded_file.name,
                    'results': comparison_result
                })
            except (IOError, ValueError) as e:
                global_parsing_errors.append(f"Error parsing '{uploaded_file.name}': {e}")
            finally:
                os.unlink(temp_file_path)
        
        # Debugging: Print session content before storing
        # print("---", "Before storing in session (compare_boms) ---")
        # print(f"Session key: {request.session.session_key}")
        # print(f"Existing session data: {request.session.items()}")

        # Store results in session
        request.session['comparison_results'] = {
            'master_bom_name': master_bom.name,
            'all_comparison_results': all_comparison_results,
            'global_parsing_errors': global_parsing_errors,
        }
        request.session.modified = True # Explicitly mark session as modified
        
        # Debugging: Print session content after storing and marking modified
        # print("---", "After storing in session (compare_boms) ---")
        # print(f"Session key: {request.session.session_key}")
        # print(f"Session data after update: {request.session.items()}")

        return redirect('comparison_summary')

    messages.error(request, "Invalid request method for comparison.")
    return redirect('home')


@login_required
def comparison_summary(request):
    # Debugging: Print session content at the start of comparison_summary
    # print("---", "Start of comparison_summary ---")
    # print(f"Session key: {request.session.session_key}")
    # print(f"Session data available: {request.session.items()}")

    # Use .get() instead of .pop() to retrieve data without removing it
    results = request.session.get('comparison_results', None)
    
    context = {
        'master_bom_name': results.get('master_bom_name') if results else None,
        'all_comparison_results': results.get('all_comparison_results') if results else [],
        'global_parsing_errors': results.get('global_parsing_errors') if results else [],
    }
    
    if not results: # If results are not in session, means no comparison was just done or session expired
        # print("---", "No comparison results found in session! ---")
        current_messages = list(messages.get_messages(request)) # Consume messages
        if not current_messages: # Only add if no other messages are pending
            messages.warning(request, "No comparison results found. Please perform a comparison first.")
        return redirect('home') 

    # print("---", "Comparison results retrieved from session. ---")
    return render(request, 'compare_results.html', context)
