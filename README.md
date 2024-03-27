# 🚂 PBR-Express
> PBR-Express is a handy tool for Houdini that makes it quick and easy to create PBR materials. Just toss in your texture files and the tool will instantly set up a material for your preferred renderer. It's all about saving time on the boring stuff, so VFX artists can focus more on getting creative with their materials. Enjoy a smooth process that turns textures into usable materials in Houdini!

## 📖 Table of Contents

   - [Showcase](#-showcase)
   - [Key-Features](#-key-features)
   - [Requirements](#-requirements)
   - [Contributing](#-contributing)
   - [Installation](#-installation)
   - [Manual](#-manual)
      - [How it works](#how-it-works)
      - [How to use](#how-to-use)
      - [Tips](#tips)
   - [Contributing](#-contributing)
      - [Foreword](#foreword)
      - [Adding missing presets](#adding-missing-presets)
      - [Adding missing texture types](#adding-missing-texture-types)
      - [Adding render engines](#adding-render-engines)
   - [Future-Plans](#-future-plans)
   - [Support](#-support)
      - [Buy Me a Coffee](#buy-me-a-coffee)
      - [Connect on Social Media](#connect-on-social-media)
      - [Share Your Experience](#share-your-experience)

## 🎬 Showcase
   
## 🔑 Key-Features
<details>
<summary><strong> Quickly create PBR materials with just a few clicks! </strong></summary>
<br>
Input your texture set, select your preferred renderer and the path to your material library and voilà! See "Manual" for more details on how to use the tool.
<br><br>
</details>

<details>
<summary><strong> Easy copy-paste installation </strong></summary>
<br>
No need to download anything, just copy and paste the raw code from PBR-Express.py as a shelf tool. See "Installation".
<br><br>
</details> 

<details>
<summary><strong> Texture-naming flexibility </strong></summary>
<br>
Supports any texture sets that have the texture type written at the end of the file name and it is separated by an underscore: e.g. `sample_texture_4k_displacement.exr`. Additionally, the resolution can be at the end of the name like in `sample_texture_displacement_4k.exr`. See "How to use" for more infos.
<br><br>
</details> 

<details>
<summary><strong> Support for different renderers </strong></summary>
<br>
The script is currently able to create materials for Karma (MTLX Surface Shader) and Mantra (Principled Shader). Nevertheless, its quite easy to add support for other render engines. See "Contributing" for more infos.
<br><br>
</details> 

<details>
<summary><strong> Bulk creation of materials </strong></summary>
<br>
See "Tips".
<br><br>
</details> 

<details>
<summary><strong> Unknown texture handling </strong></summary>
<br>
The script currently supports albedo(diffuse), ao, height(displacement), normal, roughness, metallic, alpha(opacity) and emission maps. If the script does not recognize a certain type of texture, it will ask the user if the texture should be loaded into the material anyway or be forgotten.  
<br><br>
</details> 

<details>
<summary><strong> Preset-oriented workflow </strong></summary>
<br>
Every texture providing website has its own naming convention. Some call it albedo while others call it diffuse. This tool tries to streamline the process of differentiating between all of those naming conventions and having one central data variable (`supportedTexture_data`) that is easily expandable and holds every possible variation of a certain texture name. See "How it works".
<br><br>
</details> 

<details>
<summary><strong> Expandable from the ground up </strong></summary>
<br>
The script was created with easy expansion in mind. New texture types are straightforward to expand and with a bit of Python knowledge even support for new render engines can be added without waiting for this repo to be updated. See "Contributing" for more infos.
<br><br>
</details> 

<details>
<summary><strong> Active node network detection </strong></summary>
<br>
See "Tips"
<br><br>
</details> 


## 📋 Requirements
* Houdini license of **any** kind (Apprentice, Core, Indie, FX, ...)
* Houdini 20.0.590 (_may_ work with older versions, but it's untested.)
* Python 3 comes preinstalled with Houdini (may vary for Linux/Mac; check the [official documentation](https://www.sidefx.com/docs/houdini/hom/index.html#which-python))

## 🛠️ Installation
1) Go to the [PBR-Express.py](PBR-Express.py) file
2) Copy the raw text (button on the top right)
3) Inside Houdini, go to any shelf tab and right click > `New Tool... `
4) Optional: Name your tool however you like
5) Optional: Pick a fitting icon, I use `BUTTONS_chooser_folder` or `BUTTONS_chooser_image_color`
6) Under the tab `script`, just paste the previously copied raw code
7) On the bottom right, click `Apply` & `Accept`

## 📖 Manual
### How it works
The tool uses the data from these _two main variables_ to match each input file to a known texture type and create the proper material setup for the renderer of choice.   

   `supported_renderers`: This is a simple list of all of the supported renderers.

   `supportedTextures_data`: This variable holds all of the supported texture types (METALLIC) with every variation of name it can have. (['Metallic', 'metallic', 'Metalness'])

### How to use
1. Press the shelf tool and you will be prompted with a file-chooser dialog where you can select your PBR textures.
2. Choose your preferred textures. The files have to **end** with the texture type OR have it written **after** the resolution; everything has to be separated by an **underscore**: e.g. `websiteName_4k_displacement.exr` or `sample_texture_displacement_4k.exr`.
   - Some examples of file names that won't work with the script as of now: `sample_texture_4k-color.exr` , `color_websiteName.exr`
   - If there are two or multiple files that are of the same texture type, the script will throw an error. 
   - DO NOT use any **semicolons that have a space before and after** them in your file paths. `C:/Desktop/my ; folder/texture.png` will break the script. Also, who names their folders like that? 
4. Choose the preferred renderer. 
5. Choose the material library in which the material will be created. If this dialog does not come up, that means that the script recognized your open network tab as a valid VOP network and will drop the materials there. 
> ***Some known limitations:*** If you have an open non-material VOP window open (for example an Attribute VOP node), the script will error out when trying to make the material. Also, if one tries to run the script inside a (VOP) subnetwork, it will also error out, even if the subnetwork is a valid material VOP.  

### Tips
- Use `CTRL` or `SHIFT` on the shelf tool to activate "Bulk Quick Setup". You can now input multiple texture sets. Just press "Accept" after each set and you will be prompted with the same window again. Upon pressing "Cancel", the materials will be created.
- The script writes logs to the console for every major action it takes. In the case of troubleshooting, it might be worth having a look.
- For more troubleshooting, one could uncomment the function `debugMetadata()`, which is located at the end of the script to get the metadata for each file printed to the console. This would be an example print: 

```
[DEBUG] Metadata of each selected file:
[DEBUG] Path: D:/Nextcloud/Textures/Bricks/1/TexturesCom_Bricks_Rh_2x2_1K_albedo.tif
[DEBUG] File Name: TexturesCom_Bricks_Rh_2x2_1K_albedo
[DEBUG] File Ending: albedo
[DEBUG] File Type: DIFFUSE
```



## 🤝 Contributing
### Foreword
This chapter serves as a guide for extending the script to meet your individual needs. Due to my other commitments, I won't be able to consistently add support for new renderers or texture types on a frequent basis. This is why I've designed the tool to be easily expandable, allowing anyone with some Python knowledge to incorporate support for their preferred texture providers or more niche texture types. If you choose to enhance the script in this manner, contributing to the GitHub repository would be highly valued, enabling everyone to benefit from open-source collaboration.


> _🚨 Disclaimer 🚨_ Just a heads up: this is my first attempt at a substantial script, and my programming knowledge is self-taught. While the tool does its job quite well, I can't promise that contributing will be a walk in the park. Things might not be as straightforward or intuitive; your patience and understanding are greatly appreciated!


### Adding missing texture names
This is something everyone can do with minimal Python or scripting knowledge. Just follow the already existing structure inside the variable `supportedTextures_data` and add your own name variations. 

I don't have access to every single texture providing website (nor the patience to do so), and since every website has its own naming conventions, there seem to be endless possibilities for naming variations. The more people contribute with their naming variations, the better the tool will be at recognizing every file name from every website.

### Adding missing texture types
   1. Add the name of the texture type inside `supportedTextures_data`.
   2. Add your new naming variations following the same conventions as the other texture types above.
   3. Now you need to make the actual code for the node creation inside `def nodeCreation()`. Again it's best to look at how the other texture nodes are being created and connected to other nodes. The most important variables will be:
      - set_name: The name of the texture set, e.g. For a file named `myTextures_4k_normal.png`, the set_name would be `myTextures`.
      - goalNode: This is the network where the nodes will be created.
      - file_data: This is a variable that holds the data of each selected file. Things like the path to the file, the file name, the file extension and the recognized texture type. The data would first need to be unpacked, but again, it makes sense to look at how it has been done for the other renderers. I normally did it like this:
      ```
        for metadata in file_data:
            file, name, ending, textureType = metadata      
      ```

### Adding render engines
   1. Add the name of the new render engine to `supported_renderers`.
   2. Now you just have to handle the actual node creation inside `def nodeCreation()`. See step 3. above in [Adding missing texture types](#adding-missing-texture-types). The only difference being, that you will need to create the whole material from the ground up.


## 🔮 Future Plans
- Adding support for other render engines like Vray, Arnold, Redshift, ...
- Adding support for more texture types like ~~emission~~, translucency, sss, ...
- Adding support for more types of texture names (e.g. file names that are separated by `-`)
- ~~The option to create multiple sets of materials once the script is active~~
- Some intuitive solutions for dealing with color spaces
- ~~Make adding new naming variations easier~~ 


## ❤️ Support
If you find this Houdini script helpful and want to support its ongoing development along with other tools, there are a few ways you can express your appreciation:
### Buy Me a Coffee
Thank you for contributing. [You can donate directly here.](https://www.paypal.com/donate/?hosted_button_id=Z8ER4W6ZMXTCC)
### Connect on Social Media
Stay updated on the latest developments and enjoy some memes by following me on social media. Your engagement and feedback mean a lot.
   - [Linkedin](https://www.linkedin.com/in/ccnst/) 
   - [Twitter](https://twitter.com/ccornesteanu)
   - [Artstation](https://www.artstation.com/ccornesteanu) 
### Share Your Experience
I'd love to hear how you're using the tool in your projects. Drop me a message about your experiences, challenges, or success stories. Your insights can help shape future improvements. Feel free to reach out via email or through the GitHub Issues page.

Your support, whether through a small donation or a simple message, greatly motivates me to enhance and maintain this tool for the community. Thank you for being part of this journey!

