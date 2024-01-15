# <img src="https://static.sidefx.com/images/apple-touch-icon.png" height="24" width="24" alt="Houdini Logo"> <img src="https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/community/logos/python-logo-only.png" height="25" width="20" alt="Python Logo"> PBR-Express
### _PBR-Express is a Houdini shelf tool designed to expedite the creation of PBR materials.  Simply input your texture files and the script will swiftly generate a material setup for your chosen renderer. Designed to minimize repetitive tasks, PBR-Express empowers VFX artists to dedicate more time to the creative nuances of material design. Experience a seamless workflow that converts textures into a ready-to-use material in Houdini._

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
      - [Adding missing presets](#adding-missing-presets)
      - [Adding missing texture types](#adding-missing-texture-types)
      - [Adding render engine](#adding-render-engine)
   - [Future-Plans](#-future-plans)
   - [Support](#-support)
      - [Buy Me A Coffee](#buy-me-a-coffee)
      - [Connect on Social Media](#connect-on-social-media)
      - [Share Your Experience](#share-your-experience)

## 🎬 Showcase
   
## 🔑 Key-Features
<details>
<summary><strong> Quickly create PBR materials with just a few clicks from your input files! </strong></summary>
<br>
See "How it works" for more details.
<br><br>
</details>

<details>
<summary><strong> Easy copy-paste installation </strong></summary>
<br>
No need to download anything, just copy and paste the raw code from PBR-Express.py as a shelf tool. See "Installation"
<br><br>
</details> 

<details>
<summary><strong> Texture naming flexibility </strong></summary>
<br>
Supports any texture sets that have the texture type written at the end of the file name and it is sepparated by an underscore: e.g. `sample_texture_4k_displacement.exr` OR `sample_texture_displacement_4k.exr`. See "How to use"
<br><br>
</details> 

<details>
<summary><strong> Support for different renderers </strong></summary>
<br>
The script currently able to create materials for Karma (MTLX Surface Shader) and Mantra (Principled Shader).
<br><br>
</details> 

<details>
<summary><strong> Preset oriented workflow </strong></summary>
<br>
Every texture providing website has its own naming convention. Some call it albedo while others call it diffuse. This tool tries to streamline the process of differentiating between all of those naming conventions and having one central variable (`preset_data`) that is easily expandable and holds every website name (e.g. Quixel) with the corresponding naming convention (e.g. "Albedo", "AO", "Displacement", "Normal", "Roughness")
<br><br>
</details> 

<details>
<summary><strong> Expandable from the ground up </strong></summary>
<br>
The script was created with easy expansion in mind. Not only can presets be added easily, but adding new texture types is also reasonably straightforward and with a bit of Python knowledge even support for new render engines can be added without waiting for this repo to be updated. See "Contributing" for more infos.
<br><br>
</details> 

<details>
<summary><strong> Custom naming conventions </strong></summary>
<br>
Don’t want to mess with the code to add your own preset? Choose `Custom setup` inside the main menu to be prompted with a window where you can input your own naming conventions. See "How to use" for more infos.
<br><br>
</details> 

<details>
<summary><strong> Active node network detection </strong></summary>
<br>
See "Tips"
<br><br>
</details> 

<details>
<summary><strong> Shortcut for "Quick setup" </strong></summary>
<br>
See "Tips"
<br><br>
</details> 


## 📋 Requirements
* Houdini license of **any** kind (Apprentice, Core, Indie, FX,... )
* Houdini 20.0.547+ (_may_ work with older versions but it's untested)
* Python 3, comes preinstalled with Houdini (may vary for Linux/Mac, check the [official documentation](https://www.sidefx.com/docs/houdini/hom/index.html#which-python))

## 🛠️ Installation
1) Go to the [PBR-Express.py](PBR-Express.py) file
2) Copy the raw text (button on the top right)
3) Inside Houdini, go to any shelf tap and right click > `New Tool... `
4) Optional: Name your tool however you like
5) Optional: Pick a fitting icon, I use `BUTTONS_chooser_folder` or `BUTTONS_chooser_image_color`
6) Under the tab `script` just paste the previously copied raw code
7) On the bottom right click `Apply` & `Accept`

## 📖 Manual
### How it works
The tool uses the data from these _three variables_ to match each input file to a known texture type and create the proper material setup for the renderer of choosing.   

   `preset_data`: This variable holds the name of a texture providing website and the naming conventions that they are using for each *texture type*. The order of the naming convention should always stay the same (e.g. 1st: Albedo map, 2nd: AO map, ...). If a website does not provide a certain texture type, an empty placeholder (`""`) has to be inputed instead.   
   `supportedTextures_data`: This variable (at the start of the script still empty) holds all of the supported texture types in the exact order that they should come from `preset_data`. It will later be given values by the script based on what comes in from `preset_data` while removing duplicates.  
   `supported_renderers`: This is a simple list with all of the supported renderers.

-----------------------NEED MROE INFO HERE-------------------

### How to use
- Press the shelf tool and you will be prompted with a file chooser dialog where you can select your PBR textures.
- Choose your prefered textures. The files have to **end** with the texture type OR have it written **after** the resolution; everything has to be sepparated by an **underscore**: e.g. `websiteName_4k_displacement.exr` or `sample_texture_displacement_4k.exr`.
   - Some examples of files namings that won't work with the script as of now: `sample_texture_4k-color.exr` , `color_websiteName.exr`
- The MAIN MENU will appear where you will have 3 options:
   1. **Quick Setup:** The script looks through _all_ of the possible naming conventions from `preset_data` and tries to match your input files to one of the texture types. If there are 2 files that are of the same texture type, the script will throw an error. **This is the recommanded setting for using the script.**  
   2. **Preset List:** User will be prompted with a list of all of the presets. Upon selecting one the script will comare the input files to _only_ the namings from the selected preset. This was the intended way of using the tool when it was first created.
   3. **Custom Preset:** User will be prompted with a list of all of the supported texture types. The user can now input custom namings for all of the texture types. Those will be compared to the input files. Using this option makes sense if you have a one off naming convention for a texture set and don't want to mess with the script itself. Those new namings won't get saved and you will have to input them again for each new material using this convention. When wanting to use a custom naming convention multiple times, it is recommanded that one types it into `preset_data`.
- Choose the prefered renderer. 
- Choose the material library in which the material will be created.

### Tips
- Use `CNTRL` or `SHIFT` or `ALT` or `CMD` + `CLICK` on the shelf tool to activate "Quick Setup", bypassing the MAIN MENU and saving a few clicks per material creation.
- If you already have a valid material network open, the tool won't ask for a path to a material library and will just take the active pane, saving a few clicks. 

## 🤝 Contributing
### Adding missing presets 
This is something everyone can do with minimal Python/scripting knowledge. Just follow the already existing preset structure inside the variable `preset_data` and add your own presets. The order should always stay the same, just look at the other entries for guidance. Additionally you can have a look at the next variable `supportedTextures_data`, which uses the same order. 

I dont have access to every single texture providing website and there are endless possibilities of naming variations, so the more people contribute with websites and their naming conventions, the better the tool will recognize the texture types.
### Adding missing texture types
-----------------------NEED MROE INFO HERE-------------------
### Adding render engine
-----------------------NEED MROE INFO HERE-------------------

## 🔮 Future Plans
- Support for other render engines like Vray, Arnold,  


## ❤️ Support
If you find this Houdini script useful and would like to support its continued development as well as that of other tools, there are several ways you can show your appreciation:
### Buy Me a Coffee
Your support helps fuel late-night coding sessions and keeps the creativity flowing! [You can donate directly to me here.](https://www.paypal.com/donate/?hosted_button_id=Z8ER4W6ZMXTCC)
### Connect on Social Media
Follow me on social media to stay updated on the latest developments and memes. Your engagement and feedback are invaluable.
   - [Linkedin](https://www.linkedin.com/in/ccnst/) 
   - [Twitter](https://twitter.com/ccornesteanu)
   - [Artstation](https://www.artstation.com/ccornesteanu) 
### Share Your Experience
   I'd love to hear how you are using the tool in your projects. Send me a message sharing your experiences, challenges, or success stories. Your insights can help shape future improvements.
   Feel free to reach out via Email or through the GitHub Issues page.
   
   Your support, whether through a small donation or a simple message, goes a long way in motivating me to enhance and maintain this tool for the community. Thank you for being a part of this journey!

