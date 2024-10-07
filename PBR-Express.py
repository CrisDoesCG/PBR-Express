# Documentation, full feature list and license can be found here: https://github.com/CrisDoesCG/PBR-Express

# Created by Cristian Cornesteanu
# Written and tested in Houdini Indie 20.5.332

# Last update 07. October 2024

import hou
import os
import re
import time

#   ---VARIABLES---

## List of supported renderers    
supported_renderers = [
"MaterialX",
"MaterialX (USD export optimized)",
"Mantra",
]

## List of all possible naming conventions, will check upper case and lower case
supportedTextures_data = {
    "DIFFUSE":      ['diffuse', 'diff', 'albedo', 'color', 'colour', 'basecolor', 'basecolour'],     
    "AO":           ['ambientocclusion', 'ao', 'occlusion', 'occ'],           
    "DISP":         ['disp', 'height', 'bump'],        
    "NORMAL":       ['normal', 'opengl', 'dx', 'normaldx', 'normal-ogl', 'nor'],      
    "ROUGH":        ['roughness', 'rough'],        
    "METALLIC":     ['metallic', 'metalness'],    
    "OPACITY":      ['opacity', 'alpha'],     
    "EMISSION":     ['emission', 'emissive'],   
    "REFRACTION":   ['refrac', 'refraction'],
    "SSS":          ['sss', 'subsurface', 'scattering'],  
}

## Remove duplicates from each list
for key, values in supportedTextures_data.items():
    supportedTextures_data[key] = list(set(values))

# Sort the keywords by length to prioritize longer matches
supportedTextures_data = {
    key: sorted(value, key=len, reverse=True)
    for key, value in supportedTextures_data.items()
}    


#   ---DEFINITIONS---
## System condensing this long string into a usable list 
def validFileTypes():

    valid_file_types = "*.pic, *.picZ, *.picgz, *.rat, *.tbf, *.dsm, *.picnc, *.piclc, *.rgb, *.rgba, *.sgi, *.tif, *.tif3, *.tif16, *.tif32, *.tiff, *.yuv, *.pix, *.als, *.cin, *.kdk, *.jpg, *.jpeg, *.exr, *.png, *.psd, *.psb, *.si, *.tga, *.vst, *.vtg, *.rla, *.rla16, *.rlb, *.rlb16, *.bmp, *.hdr, *.ptx, *.ptex, *.ies, *.dds, *.r16, *.r32, *.qtl"
    valid_file_types_clean = valid_file_types.replace("*","").replace(".","")
    valid_file_type_list = valid_file_types_clean.split(", ")
    
    return valid_file_type_list

## System for prompting the user with a folder chooser dialog 
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

## System for prompting the user with a file chooser dialog    
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

## System for tech-checking the files from the getFolderInput() or getFileInput() function and creatig a metadata tuple for each file. Then combining all file tuples into a metadata_list    
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

        index = read_files.index(file)

        texture_type = None
        texture_set = None

        stats_fileProcessed.append(file + str(index))

        file_path = read_root + file

        ### file extension check, UDIM handling and file naming handling (invalid_symbols are replaced with "_" so Houdini can create the nodes with proper namings)
        __temp_file_name, __temp_file_sep, file_extension = file.rpartition(".")     
        file_name = __temp_file_name     

        if file_extension not in valid_endings:
            invalid_extensions.append(file)   
            continue

        else:     
            if ".<UDIM>" in file or ".$F" in file:
                file_name = __temp_file_name.replace(".<UDIM>","").replace(".$F","")             

                file_path = file_path.replace(".$F",".<UDIM>")      

                stats_UDIMdetected.append(file_name+"."+file_extension+"_"+str(index))               

            if len(__temp_file_name.split(".")) > 1:
                last_part = __temp_file_name.split(".")[-1]
                if last_part.isdigit() and len(last_part) == 4 and last_part[0] == "1":
                    file_name = __temp_file_name.replace("."+last_part, "")
                    file_path = file_path.replace(last_part, "<UDIM>")

                    stats_UDIMdetected.append(file_name+"."+file_extension+"_"+str(index))  

        ### Invalid symbol handling
        for symbol in invalid_symbols:
            if symbol in file_name:
                file_name.replace(symbol,"_")                      

        ### Check what texture types the file matches 
        matching = []
        for key, values in supportedTextures_data.items():
            for value in values:
                # if value in file_name.lower():
                if re.search(rf"(^|_|-)({re.escape(value)})(_|-|\.|$)", file_name.lower()):                
                    texture_type = key
                    ### Take longest matching texture type and remove that from the name
                    matching.append(value)
                    if len(matching) > 1:
                        value = max(matching, key=len)
                    
                    ### Assign texture set
                    start_index = file_name.lower().find(value)
                    matching_substring = file_name[start_index:start_index + len(value)]
                    texture_set = file_name.replace(matching_substring,"").replace('--', '-').replace('__', '_')
                    if texture_set.endswith("-") or texture_set.endswith("_"):
                        texture_set = texture_set[:-1]        
                        file_sets_list.append(texture_set)                         
                   

                    
        ### Formatting texture_set string nicely
        # if texture_type is not None:
        #     texture_set.replace('--', '-').replace('__', '_')      
        #     if texture_set.endswith("-") or texture_set.endswith("_"):
        #         texture_set = texture_set[:-1]        
        #         file_sets_list.append(texture_set)    


        ### Houdini does not like long node names, this simplifies the name of the node if the file name is over 70 characters
        if len(file_name) > 70:
            file_name = texture_type                                             

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

    for m in metadata_list:
        file_path,file_name,texture_type,texture_set,file_extension = m
        # print(f"\n\t[DEBUG] File Path: {file_path}")
        # print(f"\t[DEBUG] File Name: {file_name}")
        # print(f"\t[DEBUG] File Extension: {file_extension}") 
        # print(f"\t[DEBUG] Texture Type: {texture_type}")
        # print(f"\t[DEBUG] Texture Set: {texture_set}")  

        if texture_type is None and texture_set is None:
            for tset in file_sets_list:
                if tset in file_name:
                    texture_set = tset
                    stats_redirectedTextures.append(file_name+"."+file_extension)
        if texture_type is None and texture_set is None:

            stats_hopelessTextures.append(file_name+"."+file_extension)
        else:    
            materialNames.append(texture_set)
            metadata = (file_path,file_name,texture_type,texture_set,file_extension)                    
            metadata_list_checked.append(metadata)

    # if valid is True:
    metadata_list_checked.append(metadata)                     
    return list(set(metadata_list_checked)), set(list(materialNames)), stats_fileProcessed, stats_invalidFiles, stats_UDIMdetected, list(set(stats_redirectedTextures)), stats_hopelessTextures      
    
## System for the actual node creation 
def nodeCreation(renderer, goal, file_data, set):

    # print(f"[INFO] Starting node creation for texture set: '{set}'.") 
    goalNode = hou.node(goal)
    col = hou.Color((0.98, 0.275, 0.275))
    detected_texture_types = []
    
    if renderer == "MaterialX":
        ### Create subnet with all parameters
        goalNode = goalNode.createNode("subnet",set)
        goalNode.moveToGoodPosition()
        goalNode.setMaterialFlag(True)                  

        parameters = goalNode.parmTemplateGroup()

        ### Parameters for MTLX tab filtering and solaris compatibility
        newParm_hidingFolder = hou.FolderParmTemplate("mtlxBuilder","MaterialX Builder",folder_type=hou.folderType.Collapsible)
        control_parm_pt = hou.IntParmTemplate('inherit_ctrl','Inherit from Class', 
                            num_components=1, default_value=(2,), 
                            menu_items=(['0','1','2']),
                            menu_labels=(['Never','Always','Material Flag']))
       
        
        newParam_tabMenu = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=["MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])
        class_path_pt = hou.properties.parmTemplate('vopui', 'shader_referencetype')
        class_path_pt.setLabel('Class Arc')
        class_path_pt.setDefaultExpressionLanguage((hou.scriptLanguage.Python,))
        class_path_pt.setDefaultExpression(('''n = hou.pwd()
n_hasFlag = n.isMaterialFlagSet()
i = n.evalParm('inherit_ctrl')
r = 'none'
if i == 1 or (n_hasFlag and i == 2):
    r = 'inherit'
return r'''
,))   

        ref_type_pt = hou.properties.parmTemplate('vopui', 'shader_baseprimpath')
        ref_type_pt.setDefaultValue(['/__class_mtl__/`$OS`'])
        ref_type_pt.setLabel('Class Prim Path')               

        newParm_hidingFolder.addParmTemplate(newParam_tabMenu)
        newParm_hidingFolder.addParmTemplate(control_parm_pt)  
        newParm_hidingFolder.addParmTemplate(class_path_pt)    
        newParm_hidingFolder.addParmTemplate(ref_type_pt)             

        ### Parameters for texture control
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
            if texture_type == "REFRACTION":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("transmission", MTLX_Image_Node,"out")     
            if texture_type == "SSS":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("subsurface", MTLX_Image_Node,"out")                                                                                  
                
        ### Check if there are no nodes of this texture_type 
        if "DIFFUSE" not in detected_texture_types and "AO" not in detected_texture_types:
            MTLX_multiply.destroy()                            
        if "DISP" not in detected_texture_types:
            MTLX_disp.destroy()
            MTLX_remap_disp.destroy()
        if "NORMAL" not in detected_texture_types:
            MTLX_normal.destroy()            

        # print(f"[SUCCESS] All MTLX nodes for texture set '{set}' have been created.")     
        goalNode.layoutChildren()

        return goalNode
        
    if renderer == "MaterialX (USD export optimized)":
        ### Create subnet with all parameters
        goalNode = goalNode.createNode("subnet",set)
        goalNode.moveToGoodPosition()
        goalNode.setMaterialFlag(True)                  

        parameters = goalNode.parmTemplateGroup()

        ### Parameters for MTLX tab filtering and solaris compatibility
        newParm_hidingFolder = hou.FolderParmTemplate("mtlxBuilder","MaterialX+USD Builder",folder_type=hou.folderType.Collapsible)
        control_parm_pt = hou.IntParmTemplate('inherit_ctrl','Inherit from Class', 
                            num_components=1, default_value=(2,), 
                            menu_items=(['0','1','2']),
                            menu_labels=(['Never','Always','Material Flag']))
       
        
        newParam_tabMenu = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=["MaterialX USD parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])
        class_path_pt = hou.properties.parmTemplate('vopui', 'shader_referencetype')
        class_path_pt.setLabel('Class Arc')
        class_path_pt.setDefaultExpressionLanguage((hou.scriptLanguage.Python,))
        class_path_pt.setDefaultExpression(('''n = hou.pwd()
n_hasFlag = n.isMaterialFlagSet()
i = n.evalParm('inherit_ctrl')
r = 'none'
if i == 1 or (n_hasFlag and i == 2):
    r = 'inherit'
return r'''
,))   

        ref_type_pt = hou.properties.parmTemplate('vopui', 'shader_baseprimpath')
        ref_type_pt.setDefaultValue(['/__class_mtl__/`$OS`'])
        ref_type_pt.setLabel('Class Prim Path')               

        newParm_hidingFolder.addParmTemplate(newParam_tabMenu)
        newParm_hidingFolder.addParmTemplate(control_parm_pt)  
        newParm_hidingFolder.addParmTemplate(class_path_pt)    
        newParm_hidingFolder.addParmTemplate(ref_type_pt)             

        ### Parameters for texture control
        # newParam_uvScale = hou.FloatParmTemplate("uvscale", "UV Scale", 2, default_value=(1,1))
        # newParam_uvOffset = hou.FloatParmTemplate("uvoffset", "UV Offset", 2, default_value=(0,0))
        # newParam_uvRotate = hou.FloatParmTemplate("uvrotate", "UV Rotate", 1)
        # newParam_separator = hou.SeparatorParmTemplate("separator")
        # newParam_displacement = hou.FloatParmTemplate("displacement", "Displacement", 1, default_value=(0.05,0))

        parameters.append(newParm_hidingFolder)
        # parameters.append(newParam_uvScale)
        # parameters.append(newParam_uvOffset)
        # parameters.append(newParam_uvRotate)
        # parameters.append(newParam_separator)
        # parameters.append(newParam_displacement)
        
        goalNode.setParmTemplateGroup(parameters)     

        ### Destroy pre-made nodes
        children = goalNode.allSubChildren()
        for c in children:
            if c.type().name() != "suboutput":
                c.destroy()
            else:
                subnet_output_surface = c               
    
        ### Create material, UV controls and additional nodes
        # subnet_output_surface.parm("connectorkind").set("output")
        # subnet_output_surface.parm("parmname").set("surface")
        # subnet_output_surface.parm("parmlabel").set("Surface")
        # subnet_output_surface.parm("parmtype").set("surface")

        # subnet_output_disp = goalNode.createNode("subnetconnector","displacement_output")
        # subnet_output_disp.parm("connectorkind").set("output")
        # subnet_output_disp.parm("parmname").set("displacement")
        # subnet_output_disp.parm("parmlabel").set("Displacement")
        # subnet_output_disp.parm("parmtype").set("displacement")        
        
        MTLX_StSf_Node = goalNode.createNode("mtlxstandard_surface", set)
        subnet_output_surface.setInput(0,MTLX_StSf_Node,0)

        USD_preview_Node = goalNode.createNode("usdpreviewsurface", set)
        subnet_output_surface.setInput(1,USD_preview_Node,0)        

        # MTLX_UV_Attrib = goalNode.createNode("usdprimvarreader", "UVAttrib")
        # MTLX_UV_Attrib.parm("signature").set("float2")
        # MTLX_UV_Attrib.parm("varname").set("uv")
        # MTLX_UV_Attrib.setColor(col)

        USD_UV_Attrib = goalNode.createNode("usdprimvarreader", "UVAttrib")
        USD_UV_Attrib.parm("signature").set("float2")
        USD_UV_Attrib.parm("varname").set("st")
        USD_UV_Attrib.setColor(col)        

        # MTLX_UV_Place = goalNode.createNode("mtlxplace2d", "UVControl")
        # MTLX_UV_Place.parm("scalex").setExpression('ch("../uvscalex")')
        # MTLX_UV_Place.parm("scaley").setExpression('ch("../uvscaley")')
        # MTLX_UV_Place.parm("offsetx").setExpression('ch("../uvoffsetx")')
        # MTLX_UV_Place.parm("offsety").setExpression('ch("../uvoffsety")')
        # MTLX_UV_Place.parm("rotate").setExpression('ch("../uvrotate")')
        # MTLX_UV_Place.setColor(col)
        # MTLX_UV_Place.setNamedInput("texcoord", MTLX_UV_Attrib, "result")

        # MTLX_disp = goalNode.createNode("mtlxdisplacement")
        # MTLX_disp.parm("scale").setExpression('ch("../displacement")')
        # subnet_output_disp.setNamedInput("suboutput", MTLX_disp, "out")
        
        # MTLX_remap_disp = goalNode.createNode("mtlxremap")
        # MTLX_remap_disp.parm("outlow").set("-0.5")
        # MTLX_remap_disp.parm("outhigh").set("0.5")
        # MTLX_disp.setNamedInput("displacement", MTLX_remap_disp, "out") 
        
        MTLX_multiply = goalNode.createNode("mtlxmultiply")
        MTLX_StSf_Node.setNamedInput("base_color", MTLX_multiply, "out")
        
        MTLX_normal = goalNode.createNode("mtlxnormalmap")
        MTLX_StSf_Node.setNamedInput("normal", MTLX_normal, "out")               
        
        for metadata in file_data:
            file_path,file_name,texture_type,texture_set,file_extension = metadata
            detected_texture_types.append(texture_type)
            
            ### Bulk actions like creating multiple texture nodes, connecting to UV Nodes
            MTLX_Image_Node = goalNode.createNode("mtlximage", file_name)  
            MTLX_Image_Node.parm("file").set(file_path)       

            USD_Image_Node = goalNode.createNode("usduvtexture", file_name)
            USD_Image_Node.parm("file").set(file_path)  

            USD_Image_Node.setInput(1,USD_UV_Attrib,0)                

            ### Individual actions for each texture texture_type
            if texture_type == "DIFFUSE":
                MTLX_multiply.setNamedInput("in1", MTLX_Image_Node, "out")
                USD_preview_Node.setNamedInput("diffuseColor", USD_Image_Node, "rgb")
            if texture_type == "AO":
                MTLX_multiply.setNamedInput("in2", MTLX_Image_Node, "out")
                MTLX_Image_Node.parm("signature").set("float")
                USD_preview_Node.setNamedInput("occlusion", USD_Image_Node, "r")
            if texture_type == "NORMAL":
                MTLX_normal.setNamedInput("in", MTLX_Image_Node, "out")
                MTLX_Image_Node.parm("signature").set("vector3")
                USD_preview_Node.setNamedInput("normal", USD_Image_Node, "rgb")
            if texture_type == "ROUGH":
                MTLX_StSf_Node.setNamedInput("specular_roughness", MTLX_Image_Node,"out")
                MTLX_Image_Node.parm("signature").set("float")
                USD_preview_Node.setNamedInput("roughness", USD_Image_Node, "r")
            if texture_type == "METALLIC":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("metalness", MTLX_Image_Node,"out")
                USD_preview_Node.setNamedInput("metallic", USD_Image_Node, "r")
            if texture_type == "OPACITY":
                MTLX_StSf_Node.setNamedInput("opacity", MTLX_Image_Node,"out")  
                USD_preview_Node.setNamedInput("opacity", USD_Image_Node, "r")
            if texture_type == "EMISSION":
                MTLX_Image_Node.parm("signature").set("float")
                MTLX_StSf_Node.setNamedInput("emission", MTLX_Image_Node,"out")
                USD_preview_Node.setNamedInput("emissiveColor", USD_Image_Node, "rgb")
            # if texture_type == "REFRACTION":
            #     MTLX_Image_Node.parm("signature").set("float")
            #     MTLX_StSf_Node.setNamedInput("transmission", MTLX_Image_Node,"out")     
            # if texture_type == "SSS":
            #     MTLX_Image_Node.parm("signature").set("float")
            #     MTLX_StSf_Node.setNamedInput("subsurface", MTLX_Image_Node,"out")                                                                                  
                
        ### Check if there are no nodes of this texture_type 
        if "DIFFUSE" in detected_texture_types and "AO" not in detected_texture_types:
            MTLX_multiply.destroy()                            
        # if "DISP" not in detected_texture_types:
        #     MTLX_disp.destroy()
        #     MTLX_remap_disp.destroy()
        if "NORMAL" not in detected_texture_types:
            MTLX_normal.destroy()            

        # print(f"[SUCCESS] All MTLX nodes for texture set '{set}' have been created.")     
        goalNode.layoutChildren()

        return goalNode

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
            if texture_type == "REFRACTION":
                MANTRA_principled.parm("transparency_useTexture").set(True)
                MANTRA_principled.parm("transparency_texture").set(file_path)                                             
            if texture_type == "SSS":
                MANTRA_principled.parm("sss_useTexture").set(True)
                MANTRA_principled.parm("sss_texture").set(file_path)

        return MANTRA_principled



#   ---EXECUTE DEFINITIONS---                  
print("------------------------------------------------")         
print("[INFO] Starting PBR Express.") 

## Create empty variables
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
renderer = renderHandler(supported_renderers)

## Create .txt log file
houdini_tmp = os.getenv("HOUDINI_TEMP_DIR")
houdini_file_name = os.getenv("HIPNAME")

timestamp = time.strftime("%Y%m%d-%H%M%S")
log_dir = os.path.join(houdini_tmp, houdini_file_name, "PBR-Express")
log_path = os.path.join(log_dir, f"PBR-Express_log_{timestamp}.txt")

## Ensure the directory exists
os.makedirs(log_dir, exist_ok=True)

## Write the string to the file
with open(log_path, "w") as file:
    file.write("\n---------------------------------------------------\n\n")
    file.write(f"Script is creating materials based on the preset '{renderer}' at '{goal}'...\n")    
    file.write("\n---------------------------------------------------\n\n")
    file.write("List of created materials and their content...")



## START MAIN LOOP
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

    numOfMaterials = len(materialData)
    with hou.InterruptableOperation(
        "Creating textures...", "Executing PBR-Express...", open_interrupt_dialog=True) as operation:                
        for index, (materialName, materialFiles) in enumerate(materialData.items()):
            createdMaterial = nodeCreation(renderer,goal,materialFiles,materialName)  
            createdMaterial_name = createdMaterial.name()

            ### Wite to log file
            with open(log_path, "a") as file:
                file.write(f"\n\n\n- Material: {createdMaterial_name}")
                for metadata in materialFiles:
                    file_path,file_name,texture_type,texture_set,file_extension = metadata
                    file.write(f"\n\tFile Path: {file_path}\n")
                    file.write(f"\tFile Name: {file_name}\n")
                    file.write(f"\tFile Extension: {file_extension}\n") 
                    file.write(f"\tTexture Type: {texture_type}\n")
                    file.write(f"\tTexture Set: {texture_set}\n")                  


            percent = (float(index) / float(numOfMaterials))
            operation.updateLongProgress(percent)                       
    
  


#   ---LOGGING---
## Printing errors and writing them to the log file
if len(list_stats_invalidExtensions) != 0:
    with open(log_path, "a") as file:
        file.write("\n\n---------------------------------------------------\n\n")
        file.write("List of files with invalid extensions...\n\n")  
        for entry in list_stats_invalidExtensions:
            file.write(f"\n\t{entry}\n")         

    print(f"[ERROR] Those files are not supported image files and will be ignored: {list_stats_invalidExtensions}")  

if len(list_stats_invalidTextures) > 0:
    with open(log_path, "a") as file:
        file.write("\n\n---------------------------------------------------\n\n")
        file.write("List of invalid textures...     (couldn't find any fitting texture type)\n\n")  
        for entry in list_stats_invalidTextures:
            file.write(f"\n\t{entry}\n")     

    print(f"[ERROR] Some files couldn't be recognized: {list_stats_invalidTextures}")
    print(f"[INFO] Cross-checking unrecognized textures to find potential fitting texture set...")

if len(list_stats_redirectedTextures) > 0:
    with open(log_path, "a") as file:
        file.write("\n\n---------------------------------------------------\n\n")
        file.write("List of redirected textures...\n\n")  
        for entry in list_stats_redirectedTextures:
            file.write(f"\n\t{entry}\n")     

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

print(f"\n\tLog file saved to: {log_path}")

print("\n[INFO] Ending script.")
print("------------------------------------------------")



