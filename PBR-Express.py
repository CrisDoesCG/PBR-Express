import hou
import os

#   ---THE VARIABLES---

preset_data = {

    # NAME OF THE PRESET #              # THE NAMING CONVENTION #
    "quixel.com":           ["Albedo", "AO", "Displacement", "Normal", "Roughness", "", ""],
    "textures.com":         ["albedo", "ao", "height", "normal", "roughness", "metallic", "alpha"],
    "polyhaven.com":        ["diff", "ao", "disp", "dx", "rough", "", ""],                                                  # metallic won't work since those are "arm" textures which would need special treatment
    "cgbookcase.com":       ["BaseColor", "AO", "Height", "Normal", "Roughness", "Metallic", "Opacity"],
    "freepbr.com":          ["albedo", "ao", "height", "normal-ogl", "roughness", "metallic", ""],
    "ambientcg.com":        ["Color", "AmbientOcclusion", "Displacement", "NormalDX", "Roughness", "Metalness", "Opacity"],
    "3dtextures.me":        ["basecolor", "ambientOcclusion", "height", "normal", "roughness", "metallic", "opacity"],
    "pbrmaterials.com":     ["BaseColor", "AmbientOcclusion", "Height", "Normal", "Roughness", "Metallic", "Opacity"],
    "texturecan.com":       ["color", "ao", "height", "opengl", "roughness", "metallic", "opacity"],

}


supportedTextures_data = {
    "DIFFUSE": [],      # index = 0
    "AO": [],           # index = 1
    "DISP": [],         # index = 2
    "NORMAL": [],       # index = 3
    "ROUGH": [],        # index = 4
    "METALLIC": [],     # index = 5
    "OPACITY": [],      # index = 6
}

supported_renderers = [
"Karma",
"Mantra",
]

## Fill in supportedTextures_data based on the preset_data
for key, values in preset_data.items():
    for index, value in enumerate(values):
        if index == 0:
            supportedTextures_data["DIFFUSE"].append(value)
        elif index == 1:
            supportedTextures_data["AO"].append(value)
        elif index == 2:
            supportedTextures_data["DISP"].append(value)
        elif index == 3:
            supportedTextures_data["NORMAL"].append(value)
        elif index == 4:
            supportedTextures_data["ROUGH"].append(value)
        elif index == 5:
            supportedTextures_data["METALLIC"].append(value) 
        elif index == 6:
            supportedTextures_data["OPACITY"].append(value)             

## Remove duplicates from each list
for key, values in supportedTextures_data.items():
    supportedTextures_data[key] = list(set(values))
    
    
        
#   ---DEFINITIONS---

## System for converting this long string into a usable list to be used later
def validFileTypes():

    valid_file_types = "*.pic, *.pic.Z, *.picZ, *.pic.gz, *.picgz, *.rat, *.tbf, *.dsm, *.picnc, *.piclc, *.rgb, *.rgba, *.sgi, *.tif, *.tif3, *.tif16, *.tif32, *.tiff, *.yuv, *.pix, *.als, *.cin, *.kdk, *.jpg, *.jpeg, *.exr, *.png, *.psd, *.psb, *.si, *.tga, *.vst, *.vtg, *.rla, *.rla16, *.rlb, *.rlb16, *.bmp, *.hdr, *.ptx, *.ptex, *.ies, *.dds, *.r16, *.r32, *.qtl"
    valid_file_types_clean = valid_file_types.replace("*","")
    valid_file_type_list = valid_file_types_clean.split(", ")
    
    return valid_file_type_list
    
## System for checking the files from the hou.ui.selectFile() function and creatig a metadata tuple for each file. Then combining all file tuples into a metadata_list
def textureFinder(input):
    
    if len(input) == 0:
        print("[INFO] Script has been canceled.")
        hou.ui.displayMessage("Script has been canceled.")
        exit()     
        
    input_files_clean = input.split(" ; ")
        
    metadata_list = []       
    invalid_fileTypes = []        
    file_endings = [] 
    resolutions = ["1k", "1K", "2k", "2K", "4k", "4K", "8k", "8K", "16k", "16K", "32k", "32K"]

    for file in input_files_clean:
        ### Check if files types are supported
        is_valid = False
        for element in validFileTypes():
            if file.endswith(element):
                is_valid = True
                break
        if not is_valid:
            invalid_fileTypes.append(element)
        
        ### Create metadata    
        fullname = file.split("/")[-1]
        name, extension = os.path.splitext(fullname)
        if name.split("_")[-1] in resolutions:      # If the last word after the sepparator is a resolution, fall back to the 2nd word
            ending = ending = name.split("_")[-2]
        else:
            ending = name.split("_")[-1]
        type = None           
                
        metadata = (file,name,ending,type)                
        metadata_list.append(metadata) 
        
        file_endings.append(ending)
        
    ### Error checking for invalid file types or ending duplicates        

    if len(file_endings) != len(set(file_endings)):
        print(f"[ERROR] Duplicate file endings detected.")
        hou.ui.displayMessage("Seems like you have selected duplicate file endings (multiple normal maps for example).", title=("BZZ... WRONG"))
        exit()
            
    if len(invalid_fileTypes) != 0:
        print(f"[ERROR] Those files types are not supported image files: {invalid_fileTypes}")
        print(f"[ERROR] List of supported image files: {str(validFileTypes())}")        
        hou.ui.displayMessage("Seems like one of your files is not an image file, check the console for more info.", title=("BZZ... WRONG"))
        exit()           
        
    print("[SUCCESS] Input files seem valid.")                     
    print("[SUCCESS] Metadata for each file was written.")        
    return metadata_list            
        


def metadataAssign(old_data):

    quick_list = []
    unique_type = []

    for metadata in old_data:
        file, name, ending, type = metadata
        for texture_type, aliases in supportedTextures_data.items():
            if ending in aliases:
                type = texture_type
                break 

        metadata = (file,name,ending,type)
                
        quick_list.append(metadata)  

    ### Check if there are multiple files of the same type   
    for file in quick_list:
        t = file[3]
        if t == None:       # Checking so we can have multiple files that are of the type "None"
            pass
        else:            
            if t in unique_type:
                print(f"[ERROR] Multiple files of the same type detected: {t}")
                hou.ui.displayMessage(f"Seems like you have selected multiple files of the same type, check the console for more info", title=("BZZ... WRONG"))        
                exit()
            else:
                unique_type.append(t)            

    return quick_list



def metadataCheck(naming_convention, old_data):

    check_list = []

    for metadata in old_data:
        used_names = []
        file, name, ending, type = metadata
        if ending in naming_convention:
            index = naming_convention.index(ending)

            type, values = list(supportedTextures_data.items())[index]
                  

        metadata = (file,name,ending,type)      

        check_list.append(metadata)

    print("[SUCCESS] File metadata matches to corresponding texture types.") 
    return check_list          



def debugMetadata(data):
    print("[DEBUG] Metadata of each selected file:")
    for metadata in data:
        file, name, ending, type = metadata  
        print(f"\n\t[DEBUG] Path: {file}")
        print(f"\t[DEBUG] File Name: {name}")
        print(f"\t[DEBUG] File Ending: {ending}")
        print(f"\t[DEBUG] File Type: {type}\n")   



def presetHandler():

    preset_names = list(preset_data.keys())
    
    preset_selection = hou.ui.selectFromList(preset_names, exclusive=True, title=("Preset Handler"), message=("All websites have a different naming convention for their textures. Choose one from here or type your own under 'preset_data'. More info at: "), column_header="Presets", width=500, height=200)
        
    if len(preset_selection) == 0:
        print("[INFO] Script has been canceled.")
        hou.ui.displayMessage("Script has been canceled.")
        exit()
        
    preset_selection_name = preset_names[preset_selection[0]]
    naming_convention = preset_data[preset_selection_name]
    
    print(f"[SUCCESS] A valid preset was selected: {preset_selection_name}")        
    return naming_convention    
    
    
    
def presetCustom():

    preset_list = list(supportedTextures_data.keys())

    preset_custom = hou.ui.readMultiInput("Input the endings of your texture files.", preset_list, buttons=("Go!", "Nevermind..."), help= "I am helpful text", close_choice = 1)
    
    if preset_custom[0] == 1 or all(p == "" for p in preset_custom[1]):
        print("[INFO] Script has been canceled.")
        hou.ui.displayMessage("All right then. Keep your secrets...")
        exit()
    else:
    
        naming_convention = preset_custom[1] 
        
        print("[SUCCESS] A custom preset was created")  
        return naming_convention  
    
        
        
def renderHandler(renderer_names):
    
    render_selection = hou.ui.selectFromList(renderer_names, exclusive=True, title=("Render Handler"), message=("message"), column_header="Renderers", width=500, height=200)
    
    if len(render_selection) == 0:
        hou.ui.displayMessage("Script has been canceled.")
        exit()        
    else:
        render_selection_name = renderer_names[render_selection[0]]
    
    print(f"[SUCCESS] A valid renderer has been selected: {render_selection_name}")          
    return render_selection_name

    
    
def goalSelection():
    
    ## Find active pane and use as goal if it is a valid vop network, else let the user input a destination for the nodes
    ### KNOWN BUG: IF YOU ARE INSIDE A SUBNETWORK THE SCRIPT ERRORS OUT!! 
    editors = [pane for pane in hou.ui.paneTabs() if isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab()]

    currentPane = editors[-1].currentNode()

    currentPane_path = currentPane.path() 
    currentPane_type = currentPane.childTypeCategory().name()

    if currentPane_type == "Vop":
        currentPane_parent = currentPane.parent()

        if currentPane_parent.childTypeCategory().name() == "Vop":

            goalPath = currentPane_parent.path()
            print("nice")
        else:
            goalPath = currentPane_path
        print(f"[SUCCESS] A valid destination for the nodes has been selected: {goalPath}") 

    else:
        goalPath = hou.ui.selectNode(title = "Input destination for material") 

        if len(goalPath) is None:
            print("[INFO] Script has been canceled.")
            hou.ui.displayMessage("Script has been canceled.")
            exit() 

        goalType = hou.node(goalPath).childTypeCategory().name()

        if goalType != "Vop":
            print(f"[ERROR] The selected destination is not valid for material nodes: {goalPath}") 
            hou.ui.displayMessage("The selected node destination can't be used for materials, check the console for more info.", title=("BZZ... WRONG"))
            exit()

    return goalPath
        
        

def nodeCreation(renderer, goal, file_data):

    ### Check for fauly data
    faulty_data = []
    faulty_entry = []

    for metadata in file_data:
        file, name, ending, type = metadata
        if type == None:
            faulty_data.append(file)
            faulty_entry.append(metadata)

    if len(file_data) == len(faulty_data):
        print(f"[ERROR] All files not recognized:\n{faulty_data}")
        hou.ui.displayMessage("Seems like none of the selected files could be matched to any predetermined or custom texture types. See console for info.")
        exit()

    if len(faulty_data) != 0:
        print(f"[INFO] Some files can't be properly recognized:\n{faulty_data}")
        selection = hou.ui.displayMessage("Seems like you selected some files could not be matched to any predetermined or custom texture types, should the texture nodes be created anyway? (See console for info)", buttons=("Create anyway", "Forget them"))

        # Dont create image node for unrecognized texture types if user chooses so
        if selection == 1:
            file_data = [entry for entry in file_data if entry not in faulty_entry]

    print("[SUCCESS] Starting node creation.") 
    goalNode = hou.node(goal)
    col = hou.Color((0.98, 0.275, 0.275))
    detected_texture_types = []
    
    if renderer == "Karma":
        ### Create subnet
        goalNode = goalNode.createNode("subnet",set_name)
        goalNode.moveToGoodPosition()
        
        children = goalNode.allSubChildren()
        for c in children:
            c.destroy()
    
        subnet_output_surface = goalNode.createNode("subnetconnector","surface_output")
        subnet_output_surface.parm("connectorkind").set("output")
        subnet_output_surface.parm("parmname").set("surface")
        subnet_output_surface.parm("parmlabel").set("Surface")
        subnet_output_surface.parm("parmtype").set("surface")
        
        subnet_output_disp = goalNode.createNode("subnetconnector","displacement_output")
        subnet_output_disp.parm("connectorkind").set("output")
        subnet_output_disp.parm("parmname").set("displacement")
        subnet_output_disp.parm("parmlabel").set("Displacement")
        subnet_output_disp.parm("parmtype").set("displacement")        
        
        ### Create material, UV controls and additional nodes
        MTLX_StSf_Node = goalNode.createNode("mtlxstandard_surface", set_name)
        subnet_output_surface.setNamedInput("suboutput", MTLX_StSf_Node, "out")

        MTLX_UV_Tiling = goalNode.createNode("mtlxconstant", "UVTiling")
        MTLX_UV_Tiling.parm("signature").set("vector2")
        MTLX_UV_Tiling.parm("value_vector2x").set(1)
        MTLX_UV_Tiling.parm("value_vector2y").set(1)
        MTLX_UV_Tiling.setColor(col)
        
        MTLX_UV_Offset = goalNode.createNode("mtlxconstant", "UVOffset")
        MTLX_UV_Offset.parm("signature").set("vector2")
        MTLX_UV_Offset.setColor(col)
        
        MTLX_disp = goalNode.createNode("mtlxdisplacement")
        MTLX_disp.parm("scale").set(0.2)
        subnet_output_disp.setNamedInput("suboutput", MTLX_disp, "out")
        
        MTLX_remap_disp = goalNode.createNode("mtlxremap")
        MTLX_remap_disp.parm("outlow").set("-0.5")
        MTLX_remap_disp.parm("outhigh").set("0.5")
        MTLX_disp.setNamedInput("displacement", MTLX_remap_disp, "out") 
        
        MTLX_multiply = goalNode.createNode("mtlxmultiply")
        MTLX_StSf_Node.setNamedInput("base_color", MTLX_multiply, "out")
        
        MTLX_normal = goalNode.createNode("mtlxnormalmap")
        MTLX_StSf_Node.setNamedInput("normal", MTLX_normal, "out")               
        
        for metadata in file_data:
            file, name, ending, type = metadata
            detected_texture_types.append(type)
            
            ### Bulk actions like creating multiple texture nodes, connecting to UV Nodes
            MTLX_Image_Node = goalNode.createNode("mtlxtiledimage", name)  
            MTLX_Image_Node.parm("file").set(file)
            
            MTLX_Image_Node.setNamedInput("uvtiling", MTLX_UV_Tiling, "out")
            MTLX_Image_Node.setNamedInput("uvoffset", MTLX_UV_Offset, "out")            
            
            ### Individual actions for each texture type
            if type == "DIFFUSE":
                MTLX_multiply.setNamedInput("in1", MTLX_Image_Node, "out")
            if type == "AO":
                MTLX_multiply.setNamedInput("in2", MTLX_Image_Node, "out")
                MTLX_Image_Node.parm("signature").set("float")
            if type == "DISP":
                MTLX_remap_disp.setNamedInput("in", MTLX_Image_Node, "out") 
                MTLX_Image_Node.parm("signature").set("float")
            if type == "NORMAL":
                MTLX_normal.setNamedInput("in", MTLX_Image_Node, "out")
            if type == "ROUGH":
                MTLX_StSf_Node.setNamedInput("specular_roughness", MTLX_Image_Node,"out")
                MTLX_Image_Node.parm("signature").set("float")
            if type == "METALLIC":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("metalness", MTLX_Image_Node,"out")
            if type == "OPACITY":
                # MTLX_Image_Node.parm("signature").set("float")        # For some reason that I dont understand the MTLX node wants a vector as input
                MTLX_StSf_Node.setNamedInput("opacity", MTLX_Image_Node,"out")                
                
        ### Check if there are no nodes of this type 
        if "DIFFUSE" not in detected_texture_types and "AO" not in detected_texture_types:
            MTLX_multiply.destroy()                            
        if "DISP" not in detected_texture_types:
            MTLX_disp.destroy()
            MTLX_remap_disp.destroy()
        if "NORMAL" not in detected_texture_types:
            MTLX_normal.destroy()            

        print("[SUCCESS] All MTLX nodes created.")     
        goalNode.layoutChildren()
        
    if renderer == "Mantra":
        MANTRA_principled = goalNode.createNode("principledshader::2.0",set_name)
        MANTRA_principled.moveToGoodPosition()

        for metadata in file_data:
            file, name, ending, type = metadata
            detected_texture_types.append(type)        
        
            ### Individual actions for each texture type
            if type == "DIFFUSE":
                MANTRA_principled.parm("basecolor_useTexture").set(True)
                MANTRA_principled.parm("basecolor_texture").set(file)
            if type == "AO":
                MANTRA_principled.parm("occlusion_useTexture").set(True)
                MANTRA_principled.parm("occlusion_texture").set(file)
            if type == "DISP":
                MANTRA_principled.parm("dispTex_enable").set(True)
                MANTRA_principled.parm("dispTex_texture").set(file)
            if type == "NORMAL":
                MANTRA_principled.parm("baseBumpAndNormal_enable").set(True)
                MANTRA_principled.parm("baseNormal_texture").set(file)
            if type == "ROUGH":
                MANTRA_principled.parm("rough_useTexture").set(True)
                MANTRA_principled.parm("rough_texture").set(file)
            if type == "METALLIC":
                MANTRA_principled.parm("metallic_useTexture").set(True)
                MANTRA_principled.parm("metallic_texture").set(file)  
            if type == "OPACITY":
                MANTRA_principled.parm("opaccolor_useTexture").set(True)
                MANTRA_principled.parm("opaccolor_texture").set(file)                
                

        print("[SUCCESS] All Mantra nodes created.")                          
            
#   ---EXECUTE DEFINITIONS---    
print("\n\n\n[INFO] Starting PBR Express.") 

input_files = hou.ui.selectFile(title=("Choose one of the textures or input the folder path."), file_type=hou.fileType.Image, multiple_select=True, image_chooser=True)  
set_name = os.path.splitext(os.path.basename(input_files.split(" ; ")[0]))[0].rsplit('_', 1)[0]

file_data = textureFinder(input_files)

if kwargs["shiftclick"] or kwargs["altclick"] or kwargs["ctrlclick"] or kwargs["cmdclick"]:

    quick_data = metadataAssign(file_data)                  
    
    # debugMetadata(quick_data)
    
    print("[INFO] Quick setup has been initiated through the press of SHIFT / CNTRL / ALT / CMD.")
    nodeCreation("Karma",goalSelection(),quick_data)     # Here I have decided that for my quick setup I want to set the renderer to be "Karma", change accordigly

else:

    ## Pop-up window: Choose setup type
    selection = hou.ui.displayMessage("How do you want to create your setup?", title=("MAIN MENU"),buttons=("Quick Setup", "Preset List", "Custom Preset", "Cancel"))    

    if selection == 3:
        print("[INFO] Script has been canceled.")
        hou.ui.displayMessage("Script has been canceled.")
        exit()

    elif selection == 2:
        naming_convention = presetCustom()
        custom_data = metadataCheck(naming_convention, file_data)

        # debugMetadata(custom_data)

        nodeCreation(renderHandler(supported_renderers),goalSelection(),custom_data)

    elif selection == 1:
        naming_convention = presetHandler()
        check_data = metadataCheck(naming_convention, file_data)

        # debugMetadata(check_data)

        nodeCreation(renderHandler(supported_renderers),goalSelection(),check_data)

    elif selection == 0:
        quick_data = metadataAssign(file_data) 

        # debugMetadata(quick_data)

        print("[SUCCESS] Quick setup has been initiated through the main menu")
        nodeCreation(renderHandler(supported_renderers),goalSelection(),quick_data)


