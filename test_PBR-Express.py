# Documentation, full feature list and license can be found here: https://github.com/CrisDoesCG/PBR-Express

# Created by Cristian Cornesteanu
# Written and tested in Houdini Indie 20.0.625

# Last update 3. May 2024


import hou
import os

#   ---VARIABLES---

## List of supported renderers    
supported_renderers = [
"Karma",
"Mantra",
]

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

## Remove duplicates from each list
for key, values in supportedTextures_data.items():
    supportedTextures_data[key] = list(set(values))


#   ---DEFINITIONS---
## System for prompting the user with a file chooser dialog
def validFileTypes():

    valid_file_types = "*.pic, *.picZ, *.picgz, *.rat, *.tbf, *.dsm, *.picnc, *.piclc, *.rgb, *.rgba, *.sgi, *.tif, *.tif3, *.tif16, *.tif32, *.tiff, *.yuv, *.pix, *.als, *.cin, *.kdk, *.jpg, *.jpeg, *.exr, *.png, *.psd, *.psb, *.si, *.tga, *.vst, *.vtg, *.rla, *.rla16, *.rlb, *.rlb16, *.bmp, *.hdr, *.ptx, *.ptex, *.ies, *.dds, *.r16, *.r32, *.qtl"
    valid_file_types_clean = valid_file_types.replace("*","")
    valid_file_type_list = valid_file_types_clean.split(", ")
    
    return valid_file_type_list

def getFolderInput():
    userFolderInput = hou.ui.selectFile(title=("Choose the folder containing your materials."), file_type=hou.fileType.Directory, multiple_select=True)  
    if len(userFolderInput) == 0:
        print(f"[INFO] Script has been canceled.")        
        exit()
    if " ; " in userFolderInput:
        userFolderInput = userFolderInput.split(" ; ")
    else:
        userFolderInput = [userFolderInput]

    return userFolderInput 
   
def getFileInput():    
    userFileInput = hou.ui.selectFile(title=("Choose the folder containing your materials."), file_type=hou.fileType.Image, multiple_select=True, image_chooser=True)
    if len(userFileInput) == 0:
        print(f"[INFO] Script has been canceled.")        
        exit()    
    if " ; " in userFileInput:
        userFileInput = userFileInput.split(" ; ")
    else:
        userFileInput = [userFileInput]

    return userFileInput 

## System for manually setting the destination of the material(s)
def manualGoalSelection():    
    goalPath = hou.ui.selectNode(title = "Input destination for material") 

    if goalPath is None:
        print("[INFO] Script has been canceled.")
        hou.ui.displayMessage("Script has been canceled.")
        exit() 

    goalType = hou.node(goalPath).childTypeCategory().name()

    if goalType != "Vop":
        print(f"[ERROR] The selected destination is not valid for material nodes: {goalPath}") 
        hou.ui.displayMessage("The selected node destination can't be used for materials, check the console for more info.", title=("BZZ... WRONG"))
        exit()

    print(f"[SUCCESS] A valid material path was manually selected: {goalPath}")
    return goalPath   

## System for finding active pane and use that as goal for the created nodes if it is a valid vop network, else let the user input a destination for the nodes and use manualGoalSelection()
def goalSelection():
    editors = [pane for pane in hou.ui.paneTabs() if isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab()]

    currentPane = editors[-1].currentNode()

    currentPane_path = currentPane.path()
    currentPane_parent_path = currentPane.parent().path()

    errorCount = 0

    try:
        dummy1 = hou.node(currentPane_parent_path).createNode("usdprimvarreader")  
        dummy1.destroy()
    except hou.OperationFailed:
        errorCount+=1
        try:
            dummy2 = hou.node(currentPane_path).createNode("usdprimvarreader")  
            dummy2.destroy()
        except hou.OperationFailed:
            errorCount+=1 
    
    if errorCount == 0:
        print(f"[SUCCESS] A valid material path was automatically detected: {currentPane_parent_path}")
        return currentPane_parent_path
    elif errorCount == 1: 
        print(f"[SUCCESS] A valid material path was automatically detected: {currentPane_path}")
        return currentPane_path
    elif errorCount == 2: 
        print("[INFO] A valid material path couldn't be detected, falling back to manual selection.")
        return manualGoalSelection() 

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
    invalid_symbols = [" ", "(", ")", "[", "]", "{", "}", "%", "^", "&", "*"]

    if mode == "Folder":
        for root, dirs, files in os.walk(inputFiles):         
            for file in files:
                read_files.append(file)
            read_root = root

    if mode == "File":
        __temp_path = inputFiles[0]
        read_root = __temp_path[:__temp_path.rfind("/")+1]
        __temp_files = []
        for file in inputFiles:
            __temp_file = file.split('/')[-1]
            __temp_files.append(__temp_file)

        read_files = __temp_files

    ### Check for every file in the folder if the ending is valid and if the texture type is being recognized, then create metadata tuple for each file. Then combining all file tuples into a metadata_list
    for file in read_files:

        texture_type = None
        texture_set = None
        texture_UDIM = None

        stats_fileProcessed.append(file)

        file_path = read_root + file

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

            else:
                if mode == "Folder":
                    file_name, texture_UDIM, file_extension = split_file_name
                    if not texture_UDIM.isdigit() and len(texture_UDIM) != 4 and texture_UDIM[0] != 1:
                        invalid_extensions.append(file)


                    file_path = os.path.join(read_root,file.replace(str(texture_UDIM),"<UDIM>"))      

                if mode == "File":
                    file_name, texture_UDIM, file_extension = split_file_name
                    if texture_UDIM != "<UDIM>" or texture_UDIM != "$F":
                        invalid_extensions.append(file)


                    stats_UDIMdetected.append(file_name+"."+file_extension)
                                               

            ### Invalid symbol handling
            for symbol in invalid_symbols:
                if symbol in file_name:
                    file_name.replace(symbol,"_")

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
    materialNames = []

    ### Redirecting lost textures 
    file_sets_list = list(set(file_sets_list))

    valid = False

    for m in metadata_list:
        valid=True
        file_path,file_name,texture_type,texture_set,file_extension = m
        # print(f"\n\t[DEBUG] File Path: {file_path}")
        # print(f"\t[DEBUG] File Name: {file_name}")
        # print(f"\t[DEBUG] File Extension: {file_extension}") 
        # print(f"\t[DEBUG] Texture Type: {texture_type}")
        # print(f"\t[DEBUG] Texture Set: {texture_set}\n")            
        if texture_type is None and texture_set is None:
            for tset in file_sets_list:
                if tset in file_name:
                    texture_set = tset
                    stats_redirectedTextures.append(file_name+"."+file_extension)
        if texture_type is None and texture_set is None:
            valid=False
            stats_hopelessTextures.append(file_name+"."+file_extension)
        else:    
            materialNames.append(texture_set)
            metadata = (file_path,file_name,texture_type,texture_set,file_extension)                    
            metadata_list_checked.append(metadata)

    if valid is True:
        metadata_list_checked.append(metadata)                     
        return list(set(metadata_list_checked)), set(list(materialNames)), stats_fileProcessed, stats_invalidFiles, stats_UDIMdetected, list(set(stats_redirectedTextures)), stats_hopelessTextures      
    
## System for the actual node creation 
def nodeCreation(renderer, goal, file_data, set):

    print(f"[INFO] Starting node creation for texture set: '{set}'.") 
    goalNode = hou.node(goal)
    col = hou.Color((0.98, 0.275, 0.275))
    detected_texture_types = []
    
    if renderer == "Karma":
        ### Create subnet with all parameters
        goalNode = goalNode.createNode("subnet",set)
        goalNode.moveToGoodPosition()

        parameters = goalNode.parmTemplateGroup()

        newParm_hidingFolder = hou.FolderParmTemplate("mtlxBuilder","MaterialX Builder",folder_type=hou.folderType.Collapsible)
        newParam_tabMenu = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=["karma USD ^mtlxramp* ^hmtlxramp* ^hmtlxcubicramp* MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])

        newParm_hidingFolder.addParmTemplate(newParam_tabMenu)

        newParam_uvScale = hou.FloatParmTemplate("uvscale", "UV Scale", 2, default_value=(1,1))
        newParam_uvOffset = hou.FloatParmTemplate("uvoffset", "UV Offset", 2, default_value=(0,0))
        newParam_uvRotate = hou.FloatParmTemplate("uvrotate", "UV Rotate", 1)
        newParam_separator = hou.SeparatorParmTemplate("separator")
        newParam_displacement = hou.FloatParmTemplate("displacement", "Displacement", 1, default_value=(0.05,0))

        parameters.append(newParm_hidingFolder)
        parameters.append(newParam_uvScale)
        parameters.append(newParam_uvOffset)
        parameters.append(newParam_uvRotate)
        parameters.append(newParam_separator)
        parameters.append(newParam_displacement)
        
        goalNode.setParmTemplateGroup(parameters)   

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
        
        MTLX_StSf_Node = goalNode.createNode("mtlxstandard_surface", set)
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
            file_path,file_name,texture_type,texture_set,file_extension = metadata
            detected_texture_types.append(texture_type)
            
            ### Bulk actions like creating multiple texture nodes, connecting to UV Nodes
            MTLX_Image_Node = goalNode.createNode("mtlxtiledimage", file_name)  
            MTLX_Image_Node.parm("file").set(file_path)
            
            MTLX_Image_Node.setNamedInput("texcoord", MTLX_UV_Place, "out")               
            
            ### Individual actions for each texture texture_type
            if texture_type == "DIFFUSE":
                MTLX_multiply.setNamedInput("in1", MTLX_Image_Node, "out")
            if texture_type == "AO":
                MTLX_multiply.setNamedInput("in2", MTLX_Image_Node, "out")
                MTLX_Image_Node.parm("signature").set("float")
            if texture_type == "DISP":
                MTLX_remap_disp.setNamedInput("in", MTLX_Image_Node, "out") 
                MTLX_Image_Node.parm("signature").set("float")
            if texture_type == "NORMAL":
                MTLX_normal.setNamedInput("in", MTLX_Image_Node, "out")
                MTLX_Image_Node.parm("signature").set("vector3")
            if texture_type == "ROUGH":
                MTLX_StSf_Node.setNamedInput("specular_roughness", MTLX_Image_Node,"out")
                MTLX_Image_Node.parm("signature").set("float")
            if texture_type == "METALLIC":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("metalness", MTLX_Image_Node,"out")
            if texture_type == "OPACITY":
                MTLX_StSf_Node.setNamedInput("opacity", MTLX_Image_Node,"out")  
            if texture_type == "EMISSION":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("emission", MTLX_Image_Node,"out")                                                
                
        ### Check if there are no nodes of this texture_type 
        if "DIFFUSE" not in detected_texture_types and "AO" not in detected_texture_types:
            MTLX_multiply.destroy()                            
        if "DISP" not in detected_texture_types:
            MTLX_disp.destroy()
            MTLX_remap_disp.destroy()
        if "NORMAL" not in detected_texture_types:
            MTLX_normal.destroy()            

        print(f"[SUCCESS] All MTLX nodes for texture set '{set}' have been created.")     
        goalNode.layoutChildren()
        
    if renderer == "Mantra":        # I am aware that this implementations is pretty basic, but since Karma seems to be taking over I assume that most people will use MTLX anyway
        MANTRA_principled = goalNode.createNode("principledshader::2.0",set)
        MANTRA_principled.moveToGoodPosition()

        MANTRA_principled.parm("basecolorr").set(1)
        MANTRA_principled.parm("basecolorg").set(1)
        MANTRA_principled.parm("basecolorb").set(1)
        

        for metadata in file_data:
            file_path,file_name,texture_type,texture_set,file_extension = metadata
            detected_texture_types.append(texture_type)        
        
            ### Individual actions for each texture_type
            if texture_type == "DIFFUSE":
                MANTRA_principled.parm("basecolor_useTexture").set(True)
                MANTRA_principled.parm("basecolor_texture").set(file_path)
            if texture_type == "AO":
                MANTRA_principled.parm("occlusion_useTexture").set(True)
                MANTRA_principled.parm("occlusion_texture").set(file_path)
            if texture_type == "DISP":
                MANTRA_principled.parm("dispTex_enable").set(True)
                MANTRA_principled.parm("dispTex_texture").set(file_path)
            if texture_type == "NORMAL":
                MANTRA_principled.parm("baseBumpAndNormal_enable").set(True)
                MANTRA_principled.parm("baseNormal_texture").set(file_path)
            if texture_type == "ROUGH":
                MANTRA_principled.parm("rough_useTexture").set(True)
                MANTRA_principled.parm("rough_texture").set(file_path)
            if texture_type == "METALLIC":
                MANTRA_principled.parm("metallic_useTexture").set(True)
                MANTRA_principled.parm("metallic_texture").set(file_path)  
            if texture_type == "OPACITY":
                MANTRA_principled.parm("opaccolor_useTexture").set(True)
                MANTRA_principled.parm("opaccolor_texture").set(file_path)                
            if texture_type == "EMISSION":
                MANTRA_principled.parm("emitcolor_useTexture").set(True)
                MANTRA_principled.parm("emitcolor_texture").set(file_path)                              


        print(f"[SUCCESS] All Mantra nodes for texture set '{set}' have been created.")  



#   ---EXECUTE DEFINITIONS---                  
print("------------------------------------------------")         
print("[INFO] Starting PBR Express.") 

list_stats_fileProcessed = []
list_stats_invalidTextures = []
list_stats_invalidExtensions = []
list_stats_UDIMdetected = []
list_stats_redirectedTextures = []
list_stats_hopelessTextures = []
list_stats_materialsCreated = []

selection = hou.ui.displayMessage("Choose your mode:", buttons=("File select","Folder select", "Cancel"), close_choice=2, title="PBR-Express", details="Please refer to the documentation: https://github.com/CrisDoesCG/PBR-Express", details_label="Need help?", details_expanded=False)

if selection == 2:
    print(f"[INFO] Script has been canceled.")
    exit()
elif selection == 0:
    input_short = getFileInput()
    input = [input_short]
    mode = "File"
    print(f"[INFO] Start tech-checking files, {len(input_short)} files to check...")
elif selection == 1:
    input = getFolderInput()
    if len(input) == 0:
        input = [input]
    mode = "Folder"
    print(f"[INFO] Start tech-checking files, {len(input)} directory to check...")

goal = goalSelection()

for i in input:
    data, materialNames, stats_fileProcessed, stats_invalidFiles, stats_UDIMdetected, stats_redirectedTextures, stats_hopelessTextures = techChecker(i,mode)
    invalid_textures, invalid_extensions = stats_invalidFiles

    list_stats_fileProcessed += stats_fileProcessed
    list_stats_invalidTextures += stats_invalidFiles[0]
    list_stats_invalidExtensions += stats_invalidFiles[1]
    list_stats_UDIMdetected += stats_UDIMdetected
    list_stats_redirectedTextures += stats_redirectedTextures
    list_stats_hopelessTextures += stats_hopelessTextures
    list_stats_materialsCreated += materialNames

    materialData = {}

    ### Split the texture data into groups with the material name as the name of the group
    for metadata in data:
        file_path,file_name,texture_type,texture_set,file_extension = metadata
        if texture_set not in materialData:
            materialData[texture_set] = []
        materialData[texture_set].append(metadata) 
                
    for materialName, materialFiles in materialData.items():
        nodeCreation("Karma",goal,materialFiles,materialName)  

        ## FOR DEBUGGING
        print(f"\n[DEBUG] Material: {materialName}")           
        for metadata in materialFiles:
            file_path,file_name,texture_type,texture_set,file_extension = metadata
            print(f"\n\t[DEBUG] File Path: {file_path}")
            print(f"\t[DEBUG] File Name: {file_name}")
            print(f"\t[DEBUG] File Extension: {file_extension}") 
            print(f"\t[DEBUG] Texture Type: {texture_type}")
            print(f"\t[DEBUG] Texture Set: {texture_set}\n")            
  


#   ---LOGGING---
## Printing errors
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


## Printing stats
print(f"\n\t[STATS] Total files processed: {len(list_stats_fileProcessed)}")
print(f"\t[STATS] Total UDIMs detected: {len(list_stats_UDIMdetected)}")
print(f"\t[STATS] Total unrecognized files: {(len(list_stats_invalidTextures)+len(list_stats_invalidExtensions))-len(list_stats_redirectedTextures)}")
print(f"\t[STATS] Total redirected textures: {len(list_stats_redirectedTextures)}")
print(f"\t[STATS] Total materials created: {len(list_stats_materialsCreated)}")

print("\n[INFO] Ending script.")
print("------------------------------------------------")
    
# Fix bug with UDIM folder? Alu texture not working for some reason

