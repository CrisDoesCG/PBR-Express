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

def getTextureSet():
    userInput = hou.ui.selectFile(title=("Choose the folder containing your materials."), file_type=hou.fileType.Directory, multiple_select=True)  
    return userInput    
    
## System for tech-checking the files from the getTextureSet() function and creatig a metadata tuple for each file. Then combining all file tuples into a metadata_list    
def textureFinder(inputFiles):  
    print(f"[INFO] Start tech-checking files...")
    metadata_list = []
    file_sets_list = []

    invalidExtension = []
    invalidTextures = []
    
    folder_path = inputFiles
    all_files = os.walk(folder_path)
    
    valid_endings = validFileTypes()
    
    ### Check for every file in the folder if the ending is valid and if the texture type is being recognized, then create metadata tuple for each file. Then combining all file tuples into a metadata_list
    for root, dirs, files in all_files: 
        for index, file in enumerate(files):
            texture_type = None
            texture_set = None
            texture_UDIM = None

            file_path = os.path.join(root, file)                

            ### UDIM handling
            split_file_name = file.split(".") #BUG HERE: if I try script on big folder this shits itself

            if len(split_file_name) == 2:
                file_name, file_extension = split_file_name
            else:
                file_name, texture_UDIM, file_extension = split_file_name

            ### Check if the files are valid image types
            if "." + file_extension not in valid_endings:
                invalidExtension.append(file_name+"."+file_extension)
            else: 
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
                    invalidTextures.append(file_name+"."+file_extension)                    

                ### Making UDIM files the same so they get removed further down
                if texture_UDIM is not None:
                    file_path = file_path.replace(str(texture_UDIM),"<UDIM>")

                metadata = (file_path,file_name,texture_type,texture_set,file_extension)
                metadata_list.append(metadata)

    ### Making list so we remove duplicates (for UDIM creation mainly)
    metadata_list = list(set(metadata_list)) 

    if len(invalidExtension) != 0:
        print(f"[ERROR] Those files are not supported image files and will be ignored: {invalidExtension}")  
        print(f"[INFO] Proceeding with the script.")      
    
    if len(invalidTextures) > 0:
        print(f"[ERROR] Some files couldn't be recognized: {invalidTextures}")
        print(f"[INFO] Cross-checking unrecognized textures to find potential fitting texture set...")

    metadata_list_checked = []
    noHope = []
    check = 0

    file_sets_list = list(set(file_sets_list))

    for m in metadata_list:
        file_path,file_name,texture_type,texture_set,file_extension = m
        
        if texture_type is None and texture_set is None:
            for tset in file_sets_list:
                if tset in file_name:
                    texture_set = tset
                    check =+ 1
        if texture_type is None and texture_set is None:
            noHope.append(file_name+"."+file_extension)
        else:    
            metadata = (file_path,file_name,texture_type,texture_set,file_extension)                    
            metadata_list_checked.append(metadata)

    if check > 0:
        print(f"[SUCCESS] Some invalid textures could be grouped to a texture set.")    
    if len(noHope) > 0:
        print(f"[ERROR] Those files couldn't be associated with any texture sets and will be ignored: {noHope}")  
        print(f"[INFO] Proceeding with the script.")                   

    if len(metadata_list_checked) == 0:
        print(f"[ERROR] No valid texture files could be found. Exiting script.")
        exit()
    else:
        print("[SUCCESS] Metadata for every valid texture file was written.")             
        return metadata_list_checked        
   
      
print("------------------------------------------------")         
print("[INFO] Starting PBR Express.") 

data = textureFinder(getTextureSet())

# for metadata in data:
#     file_path,file_name,texture_type,texture_set,file_extension = metadata
#     print(f"\n\t[DEBUG] File Path: {file_path}")
#     print(f"\t[DEBUG] File Name: {file_name}")
#     print(f"\t[DEBUG] File Extension: {file_extension}") 
#     print(f"\t[DEBUG] Texture Type: {texture_type}")
#     print(f"\t[DEBUG] Texture Set: {texture_set}\n")         

