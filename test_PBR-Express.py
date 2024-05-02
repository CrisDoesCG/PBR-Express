import hou
import os

## List of all possible naming conventions
supportedTextures_data = {
    "DIFFUSE":      ['diffuse', 'Diffuse', 'diff', 'Diff', 'Albedo', 'albedo', 'color', 'Color', 'BaseColor', 'basecolor'],     
    "AO":           ['ambientOcclusion', 'AmbientOcclusion', 'AO', 'ao'],           
    "DISP":         ['disp', 'Displacement', 'Height', 'height'],        
    "NORMAL":       ['Normal', 'normal', 'opengl', 'dx', 'NormalDX', 'normal-ogl', 'nor'],      
    "ROUGH":        ['roughness', 'Roughness', 'rough'],        
    "METALLIC":     ['Metallic', 'metallic', 'Metalness'],    
    "OPACITY":      ['opacity', 'alpha', 'Opacity'],     
    "EMISSION":     ['Emission', 'emission', 'emissive'],     
}


def validFileTypes():

    valid_file_types = "*.pic, *.picZ, *.picgz, *.rat, *.tbf, *.dsm, *.picnc, *.piclc, *.rgb, *.rgba, *.sgi, *.tif, *.tif3, *.tif16, *.tif32, *.tiff, *.yuv, *.pix, *.als, *.cin, *.kdk, *.jpg, *.jpeg, *.exr, *.png, *.psd, *.psb, *.si, *.tga, *.vst, *.vtg, *.rla, *.rla16, *.rlb, *.rlb16, *.bmp, *.hdr, *.ptx, *.ptex, *.ies, *.dds, *.r16, *.r32, *.qtl"
    valid_file_types_clean = valid_file_types.replace("*","")
    valid_file_type_list = valid_file_types_clean.split(", ")
    
    return valid_file_type_list

def getFolderInput():
    userFolderInput = hou.ui.selectFile(title=("Choose the folder containing your materials."), file_type=hou.fileType.Directory, multiple_select=True)  
    if " ; " in userFolderInput:
        userFolderInput = userFolderInput.split(" ; ")
    else:
        userFolderInput = [userFolderInput]

    return userFolderInput 
   
def getFileInput():    
    userFileInput = hou.ui.selectFile(title=("Choose the folder containing your materials."), file_type=hou.fileType.Image, multiple_select=True, image_chooser=True)
    if " ; " in userFileInput:
        userFileInput = userFileInput.split(" ; ")
    else:
        userFileInput = [userFileInput]
    return userFileInput 

## System for tech-checking the files from the getFolderInput() function and creatig a metadata tuple for each file. Then combining all file tuples into a metadata_list    
def techChecker(inputFiles,mode): 

    metadata_list = []
    file_sets_list = []

    stats_fileProcessed = []
    stats_UDIMdetected = []
    stats_redirectedTextures = []
    stats_invalidFiles = []

    invalid_extensions = []
    invalid_textures = []

    valid_endings = validFileTypes()    

    read_files = []
    read_root = "/"

    if mode == "Folder":
        for root, dirs, files in os.walk(inputFiles):         
            for file in files:
                read_files.append(file)
            read_root = root

    elif mode == "File":
        read_root = os.path.dirname(inputFiles[0])
        read_files = [file for file in map(os.path.basename, inputFiles)]

    ### Check for every file in the folder if the ending is valid and if the texture type is being recognized, then create metadata tuple for each file. Then combining all file tuples into a metadata_list
    for index, file in enumerate(read_files):
        texture_type = None
        texture_set = None
        texture_UDIM = None

        stats_fileProcessed.append(file)

        file_path = os.path.join(read_root, file)              

        ### UDIM handling
        split_file_name = file.split(".")
        temp_file_name = split_file_name[0]
        temp_file_extension = split_file_name[-1]

        ### Check if the files are valid image types, if they are UDIM textures, stats_redirectedTextures if those UDIMs are valid, else invalid
        if len(split_file_name) < 2 or len(split_file_name) > 3 or "." + temp_file_extension not in valid_endings:
            invalid_extensions.append(file)
        else:
            if len(split_file_name) == 2:
                file_name, file_extension = split_file_name

            if len(split_file_name) == 3:
                file_name, texture_UDIM, file_extension = split_file_name
                if not texture_UDIM.isdigit() and len(texture_UDIM) != 4 and texture_UDIM[0] != 1:
                    invalid_extensions.append(file)
                    break

                stats_UDIMdetected.append(file_name+"."+file_extension)
                file_path = os.path.join(read_root,file.replace(str(texture_UDIM),"<UDIM>"))

            ### Check what texture types the file matches
            matching = []
            for key, values in supportedTextures_data.items():
                for value in values:
                    if value in file_name:
                        texture_type = key
                        
                        ### Take longest matching texture type and remove that from the name
                        matching.append(value)
                        if len(matching) > 1:
                            value = max(matching, key=len)
                        
                        ### Assign texture set
                        texture_set = file_name.replace(value,"")
                        
            ### Formatting texture_set string nicely
            if texture_type is not None:
                texture_set.replace('--', '-').replace('__', '_')      
                if texture_set.endswith("-") or texture_set.endswith("_"):
                    texture_set = texture_set[:-1]        
                    file_sets_list.append(texture_set)    
            else:
                invalid_textures.append(file_name+"."+file_extension)                    

            metadata = (file_path,file_name,texture_type,texture_set,file_extension)
            metadata_list.append(metadata)

    stats_invalidFiles = invalid_textures, invalid_extensions

    ### Making list so we remove duplicates (for UDIM creation mainly)
    metadata_list = list(set(metadata_list)) 

    metadata_list_checked = []
    stats_hopelessTextures = []


    ### Redirecting lost textures 
    file_sets_list = list(set(file_sets_list))

    valid = False

    for m in metadata_list:
        valid=True
        file_path,file_name,texture_type,texture_set,file_extension = m
        
        if texture_type is None and texture_set is None:
            for tset in file_sets_list:
                if tset in file_name:
                    texture_set = tset
                    stats_redirectedTextures.append(file_name+"."+file_extension)
        if texture_type is None and texture_set is None:
            valid=False
            stats_hopelessTextures.append(file_name+"."+file_extension)
        else:    
            metadata = (file_path,file_name,texture_type,texture_set,file_extension)                    
            metadata_list_checked.append(metadata)

    if valid is True:
        metadata_list_checked.append(metadata)                     
        return metadata_list_checked, stats_fileProcessed, stats_invalidFiles, stats_UDIMdetected, list(set(stats_redirectedTextures)), stats_hopelessTextures      
   
      
print("------------------------------------------------")         
print("[INFO] Starting PBR Express.") 

list_stats_fileProcessed = []
list_stats_invalidTextures = []
list_stats_invalidExtensions = []
list_stats_UDIMdetected = []
list_stats_redirectedTextures = []
list_stats_hopelessTextures = []

selection = hou.ui.displayMessage("Choose your mode:", buttons=("File select","Folder select", "Cancel"), close_choice=2, title="PBR-Express", details="Please refer to the documentation: https://github.com/CrisDoesCG/PBR-Express", details_label="Need help?", details_expanded=False)

if selection == 0:
    input_short = getFileInput()
    input = [input_short]
    mode = "File"
    print(f"[INFO] Start tech-checking files, {len(input_short)} files to check...")
elif selection == 1:
    input = getFolderInput()
    mode = "Folder"
    print(f"[INFO] Start tech-checking files, {len(input)} folder(s) to check...")
elif selection < 0:
    print(f"[INFO] Script has been canceled.")
    exit()

for i in input:

    data, stats_fileProcessed, stats_invalidFiles, stats_UDIMdetected, stats_redirectedTextures, stats_hopelessTextures = techChecker(i,mode)
    invalid_textures, invalid_extensions = stats_invalidFiles
    
    list_stats_fileProcessed += stats_fileProcessed
    list_stats_invalidTextures += stats_invalidFiles[0]
    list_stats_invalidExtensions += stats_invalidFiles[1]
    list_stats_UDIMdetected += stats_UDIMdetected
    list_stats_redirectedTextures += stats_redirectedTextures
    list_stats_hopelessTextures += stats_hopelessTextures

    for metadata in data:
        file_path,file_name,texture_type,texture_set,file_extension = metadata


if len(list_stats_invalidExtensions) != 0:
    print(f"[ERROR] Those files are not supported image files and will be ignored: {list_stats_invalidExtensions}")  

if len(list_stats_invalidTextures) > 0:
    print(f"[ERROR] Some files couldn't be recognized: {list_stats_invalidTextures}")
    print(f"[INFO] Cross-checking unrecognized textures to find potential fitting texture set...")

if len(list_stats_redirectedTextures) > 0:
    print(f"[SUCCESS] Some invalid textures could be redirected to a fitting texture set.") 

if len(list_stats_hopelessTextures) > 0:
    print(f"[ERROR] Those files couldn't be associated with any texture sets and will be ignored: {list_stats_hopelessTextures}")  
    print(f"[INFO] Proceeding with the script.")                   





# for metadata in data:
#     file_path,file_name,texture_type,texture_set,file_extension = metadata
#     print(f"\n\t[DEBUG] File Path: {file_path}")
#     print(f"\t[DEBUG] File Name: {file_name}")
#     print(f"\t[DEBUG] File Extension: {file_extension}") 
#     print(f"\t[DEBUG] Texture Type: {texture_type}")
#     print(f"\t[DEBUG] Texture Set: {texture_set}\n") 
     

print(f"\n\t[STATS] Total files processed: {len(list_stats_fileProcessed)}")
print(f"\t[STATS] Total UDIMs detected: {len(list_stats_UDIMdetected)}")
print(f"\t[STATS] Total unrecognized files: {(len(list_stats_invalidTextures)+len(list_stats_invalidExtensions))-len(list_stats_redirectedTextures)}")
print(f"\t[STATS] Total redirected textures: {len(list_stats_redirectedTextures)}")

print("\n[INFO] Ending script.")
print("------------------------------------------------")
    



