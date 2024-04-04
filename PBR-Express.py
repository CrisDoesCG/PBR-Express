# Documentation, full feature list and license can be found here: https://github.com/CrisDoesCG/PBR-Express

# Created by Cristian Cornesteanu
# Written and tested in Houdini Indie 20.0.625



import hou
import os

#   ---VARIABLES---

## List of supported renderers    
supported_renderers = [
"Karma",
"Mantra",
]

## List of all possible
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

## Remove duplicates from each list
for key, values in supportedTextures_data.items():
    supportedTextures_data[key] = list(set(values))





#   ---DEFINITIONS---
## System for prompting the user with a file chooser dialog
def getTextureSet():
    userInput = hou.ui.selectFile(title=("Choose one of the textures or input the folder path."), file_type=hou.fileType.Image, multiple_select=True, image_chooser=True)  
    return userInput



## System for converting this long string into a usable list to be used later
def validFileTypes():

    valid_file_types = "*.pic, *.pic.Z, *.picZ, *.pic.gz, *.picgz, *.rat, *.tbf, *.dsm, *.picnc, *.piclc, *.rgb, *.rgba, *.sgi, *.tif, *.tif3, *.tif16, *.tif32, *.tiff, *.yuv, *.pix, *.als, *.cin, *.kdk, *.jpg, *.jpeg, *.exr, *.png, *.psd, *.psb, *.si, *.tga, *.vst, *.vtg, *.rla, *.rla16, *.rlb, *.rlb16, *.bmp, *.hdr, *.ptx, *.ptex, *.ies, *.dds, *.r16, *.r32, *.qtl"
    valid_file_types_clean = valid_file_types.replace("*","")
    valid_file_type_list = valid_file_types_clean.split(", ")
    
    return valid_file_type_list
    


## System for checking the files from the hou.ui.selectFile() function and creatig a metadata tuple for each file. Then combining all file tuples into a metadata_list
def textureFinder(inputFiles):
    
    if len(inputFiles) == 0:
        print("[INFO] Script has been canceled.")
        hou.ui.displayMessage("Script has been canceled.")
        exit()     
        
    input_files_clean = inputFiles.split(" ; ")
        
    metadata_list = []       
    invalid_fileTypes = []        
    file_endings = [] 
    resolutions = ["1k", "1K", "2k", "2K", "4k", "4K", "6k", "6K", "8k", "8K", "16k", "16K", "32k", "32K"]

    for file in input_files_clean:
        ### Check if files types are supported
        is_valid = False
        validFileEndings = validFileTypes()
        for element in validFileEndings:
            if file.endswith(element):
                is_valid = True
                break
        if not is_valid:
            invalid_fileTypes.append(element)
        
        ### Create metadata    
        fullname = file.split("/")[-1]
        name, extension = os.path.splitext(fullname)
        if name.split("_")[-1] in resolutions:      # If the last word after the sepparator is a resolution from the list above, fall back to the 2nd word
            ending = ending = name.split("_")[-2]
        else:
            ending = name.split("_")[-1]
        textureType = None           
                
        metadata = (file,name,ending,textureType)                
        metadata_list.append(metadata) 
        
        file_endings.append(ending)


    ### Error checking for invalid file types or ending duplicates
    ### Count occurrences of each element
    file_counts = {}
    for ending in file_endings:
        if ending in file_counts:
            file_counts[ending] += 1
        else:
            file_counts[ending] = 1

    ### Print duplicates
    duplicates = {key: value for key, value in file_counts.items() if value > 1}
    if duplicates:
        print(f"[ERROR] Duplicate file endings detected.")
        hou.ui.displayMessage("Seems like you have selected duplicate file endings (multiple normal maps for example).", title=("BZZ... WRONG"))
        exit()
            
    if len(invalid_fileTypes) != 0:
        print(f"[ERROR] Those files types are not supported image files: {invalid_fileTypes}")
        print(f"[ERROR] List of supported image files: {str(validFileTypes())}")        
        hou.ui.displayMessage("Seems like one of your files is not an image file, check the console for more info.", title=("BZZ... WRONG"))
        exit()           

    print("\n[SUCCESS] Input files seem valid.")                     
    print("[SUCCESS] Metadata for each file was written.")        
    return metadata_list            



## System for cleaning up the data from the tuple created in textureFinder()
def metadataAssign(old_data):

    quick_list = []
    unique_type = []

    for metadata in old_data:
        file, name, ending, textureType = metadata
        for texture_type, aliases in supportedTextures_data.items():
            if ending in aliases:
                textureType = texture_type
                break 

        metadata = (file,name,ending,textureType)
                
        quick_list.append(metadata)  

    ### Check if there are multiple files of the same textureType   
    for file in quick_list:
        t = file[3]
        if t == None:       # Checking so we can have multiple files that are of the textureType "None"
            pass
        else:            
            if t in unique_type:
                print(f"[ERROR] Multiple files of the same textureType detected: {t}")
                hou.ui.displayMessage(f"Seems like you have selected multiple files of the same textureType, check the console for more info", title=("BZZ... WRONG"))        
                exit()
            else:
                unique_type.append(t)            

    return quick_list



## System for printing out the tuple that was created in textureFinder(), this is only used for debugging
def debugMetadata(data):
    print("[DEBUG] Metadata of each selected file:")
    for metadata in data:
        file, name, ending, textureType = metadata  
        print(f"\n\t[DEBUG] Path: {file}")
        print(f"\t[DEBUG] File Name: {name}")
        print(f"\t[DEBUG] File Ending: {ending}")
        print(f"\t[DEBUG] Texture Type: {textureType}\n")   



## System for promting the user with a window in which the desired render engine can be selected  
def renderHandler(renderer_names):
    
    render_selection = hou.ui.selectFromList(renderer_names, exclusive=True, title=("Render Handler"), message=("For which renderer should the material be created?"), column_header="Renderers", width=500, height=200)
    
    if len(render_selection) == 0:
        hou.ui.displayMessage("Script has been canceled.")
        exit()        
    else:
        render_selection_name = renderer_names[render_selection[0]]
    
    print(f"[SUCCESS] A valid renderer has been selected: {render_selection_name}")          
    return render_selection_name

    

## System for creating finding active pane and use that as goal for the created nodes if it is a valid vop network, else let the user input a destination for the nodes
def goalSelection():
    ### KNOWN BUG: IF YOU ARE INSIDE A SUBNETWORK THE SCRIPT ERRORS OUT!! 
    ### KNOWN BUG: IF YOU ARE INSIDE A NORMAL VOP NETWORK THE SCRIPT ERRORS OUT!! 
    editors = [pane for pane in hou.ui.paneTabs() if isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab()]

    currentPane = editors[-1].currentNode()

    currentPane_path = currentPane.path() 
    currentPane_type = currentPane.childTypeCategory().name()

    if currentPane_type == "Vop":
        currentPane_parent = currentPane.parent()

        if currentPane_parent.childTypeCategory().name() == "Vop":

            goalPath = currentPane_parent.path()

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
        


## System for the actual node creation 
def nodeCreation(renderer, goal, file_data):

    ### Check for fauly data
    faulty_data = []
    faulty_entry = []

    for metadata in file_data:
        file, name, ending, textureType = metadata
        if textureType == None:
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

    print(f"[SUCCESS] Starting node creation for texture set: '{set_name}'.") 
    goalNode = hou.node(goal)
    col = hou.Color((0.98, 0.275, 0.275))
    detected_texture_types = []
    
    if renderer == "Karma":
        ### Create subnet with all parameters
        goalNode = goalNode.createNode("subnet",set_name)
        goalNode.moveToGoodPosition()

        parameters = goalNode.parmTemplateGroup()

        newParm_hidingFolder = hou.FolderParmTemplate("mtlxBuilder","MaterialX Builder",folder_type=hou.folderType.Collapsible)
        newParam_tabMenu = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1)

        newParm_hidingFolder.addParmTemplate(newParam_tabMenu)

        newParam_uvScale = hou.FloatParmTemplate("uvscale", "UV Scale", 2, default_value=(1,1))
        newParam_uvOffset = hou.FloatParmTemplate("uvoffset", "UV Offset", 2, default_value=(0,0))
        newParam_uvRotate = hou.FloatParmTemplate("uvrotate", "UV Rotate", 1)
        newParam_separator = hou.SeparatorParmTemplate("separator")
        newParam_displacement = hou.FloatParmTemplate("displacement", "Displacement", 1)

        parameters.append(newParm_hidingFolder)
        parameters.append(newParam_uvScale)
        parameters.append(newParam_uvOffset)
        parameters.append(newParam_uvRotate)
        parameters.append(newParam_separator)
        parameters.append(newParam_displacement)
        
        goalNode.setParmTemplateGroup(parameters) 
        goalNode.parm("tabmenumask").set("MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput")     
        goalNode.parm("displacement").set(0.05)

        ### Destroy pre-made nodes
        children = goalNode.allSubChildren()
        for c in children:
            c.destroy()
    
        ### Create material, UV controls and additional nodes
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
        
        MTLX_StSf_Node = goalNode.createNode("mtlxstandard_surface", set_name)
        subnet_output_surface.setNamedInput("suboutput", MTLX_StSf_Node, "out")

        MTLX_UV_Attrib = goalNode.createNode("usdprimvarreader", "UVAttrib")
        MTLX_UV_Attrib.parm("signature").set("float2")
        MTLX_UV_Attrib.parm("varname").set("uv")
        MTLX_UV_Attrib.setColor(col)

        MTLX_UV_Place = goalNode.createNode("mtlxplace2d", "UVControl")
        MTLX_UV_Place.parm("scalex").setExpression('ch("../uvscalex")')
        MTLX_UV_Place.parm("scaley").setExpression('ch("../uvscaley")')
        MTLX_UV_Place.parm("offsetx").setExpression('ch("../uvoffsetx")')
        MTLX_UV_Place.parm("offsety").setExpression('ch("../uvoffsety")')
        MTLX_UV_Place.parm("rotate").setExpression('ch("../uvrotate")')
        MTLX_UV_Place.setColor(col)
        MTLX_UV_Place.setNamedInput("texcoord", MTLX_UV_Attrib, "result")

        MTLX_disp = goalNode.createNode("mtlxdisplacement")
        MTLX_disp.parm("scale").setExpression('ch("../displacement")')
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
            file, name, ending, textureType = metadata
            detected_texture_types.append(textureType)
            
            ### Bulk actions like creating multiple texture nodes, connecting to UV Nodes
            MTLX_Image_Node = goalNode.createNode("mtlxtiledimage", name)  
            MTLX_Image_Node.parm("file").set(file)
            
            MTLX_Image_Node.setNamedInput("texcoord", MTLX_UV_Place, "out")               
            
            ### Individual actions for each texture textureType
            if textureType == "DIFFUSE":
                MTLX_multiply.setNamedInput("in1", MTLX_Image_Node, "out")
            if textureType == "AO":
                MTLX_multiply.setNamedInput("in2", MTLX_Image_Node, "out")
                MTLX_Image_Node.parm("signature").set("float")
            if textureType == "DISP":
                MTLX_remap_disp.setNamedInput("in", MTLX_Image_Node, "out") 
                MTLX_Image_Node.parm("signature").set("float")
            if textureType == "NORMAL":
                MTLX_normal.setNamedInput("in", MTLX_Image_Node, "out")
                MTLX_Image_Node.parm("signature").set("vector3")
            if textureType == "ROUGH":
                MTLX_StSf_Node.setNamedInput("specular_roughness", MTLX_Image_Node,"out")
                MTLX_Image_Node.parm("signature").set("float")
            if textureType == "METALLIC":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("metalness", MTLX_Image_Node,"out")
            if textureType == "OPACITY":
                MTLX_StSf_Node.setNamedInput("opacity", MTLX_Image_Node,"out")  
            if textureType == "EMISSION":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("emission", MTLX_Image_Node,"out")                                                
                
        ### Check if there are no nodes of this textureType 
        if "DIFFUSE" not in detected_texture_types and "AO" not in detected_texture_types:
            MTLX_multiply.destroy()                            
        if "DISP" not in detected_texture_types:
            MTLX_disp.destroy()
            MTLX_remap_disp.destroy()
        if "NORMAL" not in detected_texture_types:
            MTLX_normal.destroy()            

        print(f"[SUCCESS] All MTLX nodes for texture set '{set_name}' have been created.")     
        goalNode.layoutChildren()
        
    if renderer == "Mantra":        # I am aware that this implementations is pretty basic, but since Karma seems to be taking over I assume that most people will use MTLX anyway
        MANTRA_principled = goalNode.createNode("principledshader::2.0",set_name)
        MANTRA_principled.moveToGoodPosition()

        MANTRA_principled.parm("basecolorr").set(1)
        MANTRA_principled.parm("basecolorg").set(1)
        MANTRA_principled.parm("basecolorb").set(1)
        

        for metadata in file_data:
            file, name, ending, textureType = metadata
            detected_texture_types.append(textureType)        
        
            ### Individual actions for each texture textureType
            if textureType == "DIFFUSE":
                MANTRA_principled.parm("basecolor_useTexture").set(True)
                MANTRA_principled.parm("basecolor_texture").set(file)
            if textureType == "AO":
                MANTRA_principled.parm("occlusion_useTexture").set(True)
                MANTRA_principled.parm("occlusion_texture").set(file)
            if textureType == "DISP":
                MANTRA_principled.parm("dispTex_enable").set(True)
                MANTRA_principled.parm("dispTex_texture").set(file)
            if textureType == "NORMAL":
                MANTRA_principled.parm("baseBumpAndNormal_enable").set(True)
                MANTRA_principled.parm("baseNormal_texture").set(file)
            if textureType == "ROUGH":
                MANTRA_principled.parm("rough_useTexture").set(True)
                MANTRA_principled.parm("rough_texture").set(file)
            if textureType == "METALLIC":
                MANTRA_principled.parm("metallic_useTexture").set(True)
                MANTRA_principled.parm("metallic_texture").set(file)  
            if textureType == "OPACITY":
                MANTRA_principled.parm("opaccolor_useTexture").set(True)
                MANTRA_principled.parm("opaccolor_texture").set(file)                
            if textureType == "EMISSION":
                MANTRA_principled.parm("emitcolor_useTexture").set(True)
                MANTRA_principled.parm("emitcolor_texture").set(file)                              


        print(f"[SUCCESS] All Mantra nodes for texture set '{set_name}' have been created.")                           
            




#   ---EXECUTE DEFINITIONS---   
print("------------------------------------------------")         
print("[INFO] Starting PBR Express.") 

if kwargs["shiftclick"] or kwargs["ctrlclick"]:
    check = 1
    input_texture_sets = []

    print("[INFO] Bulk Textures setup has been initiated through the press of SHIFT / CNTRL.")

    while check > 0:
        input_files = getTextureSet()
        check = len(input_files)

        if check > 0:
            input_texture_sets.append(input_files)

    renderer = renderHandler(supported_renderers)

    for set in input_texture_sets:
        set_name = os.path.splitext(os.path.basename(set.split(" ; ")[0]))[0].rsplit('_', 1)[0]
        file_data = textureFinder(set)
        quick_data = metadataAssign(file_data)
        nodeCreation(renderer,goalSelection(),quick_data)   
     
    print("\n[INFO] Ending script")
    print("------------------------------------------------")      

else:
    
    input_files = getTextureSet()
    set_name = os.path.splitext(os.path.basename(input_files.split(" ; ")[0]))[0].rsplit('_', 1)[0]

    file_data = textureFinder(input_files)

    quick_data = metadataAssign(file_data)                  
    
    # debugMetadata(quick_data)
    
    print("[INFO] Quick setup has been initiated.")
    nodeCreation(renderHandler(supported_renderers),goalSelection(),quick_data)    
    print("\n[INFO] Ending script")
    print("------------------------------------------------")


