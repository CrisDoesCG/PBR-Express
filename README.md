# <img src="https://static.sidefx.com/images/apple-touch-icon.png" height="24" width="24" alt="Houdini Logo"> <img src="https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/community/logos/python-logo-only.png" height="25" width="20" alt="Python Logo"> PBR-Express
### _A Houdini shelf tool that creates PBR materials for various renderers from the input textures._

## 📖 Table of Contents

## 🎬 Showcase
   
## 🔑 Key-Features
* **Quickly create PBR materials with just a few clicks from your input files!**
* **Easy copy-paste installation**
* **Texture naming flexibility:** Supports any texture files that have the texture type written at the end of the file name and it is sepparated by an underscore: e.g. `sample_texture_4k_displacement.exr`
* **Support for different renderers:** Right now you can choose between creating a **Karma** or **Mantra** PBR material.
* **Preset oriented workflow:** Every texture providing website has its own naming convention. Some call it albedo while others call it diffuse. This tool tries to streamline the process of differentiating between all of those naming conventions and having one central variable (`preset_data`) that is easily expandable and holds every website name (e.g. Quixel) with the corresponding naming convention (e.g. "Albedo", "AO", "Displacement", "Normal", "Roughness") 
* **Expandable from the ground up:** The script was created with easy expansion in mind. Not only can presets be added easily, but adding new texture types is also reasonably straightforward and with a bit of Python knowledge even support for new render engines can be added without waiting for this repo to be updated. See [Contributing](#-Contributing)   
* **Custom naming conventions:** Don’t want to mess with the code to add your own preset? Choose `Custom setup` inside the main menu to be prompted with a window where you can input your own naming conventions. (NOTE: Those setups won't get saved and you will have to input them for each new material)
* **Smart context detection:** If you already have a valid material network open, the tool won't ask the user for a path to create the material and will just take the active pane, saving a few clicks. 
* **Quick setup:** Use `CNTRL` or `SHIFT` or `ALT` or `CMD` + `CLICK` on the shelf tool to activate "Quick Setup", bypassing the main menu and saving 2+ clicks per material creation! 

## 📋 Requirements
* Houdini license of **any** kind (Apprentice, Core, Indie, FX,... )
* Houdini 20.0.547+ (_may_ work with older versions but it's untested)
* Python 3 (comes preinstalled with Houdini)

## 🛠️ Installation
1) Go to the [PBR-Express.py](PBR-Express.py) file
2) Copy the raw text (button on the top right)
3) Inside Houdini, go to any shelf tap and right click > `New Tool... `
4) Optional: Name your tool however you like
5) Optional: Pick a fitting icon
6) Under the tab `script` just paste the previously copied raw code
7) On the bottom right click `Apply` & `Accept`

## 🤔 How it works

## 🤝 Contributing
### Adding missing presets 
* This is something everyone can do with minimal Python/scripting knowledge. Just follow the structure inside `preset_data` and add the name of your.... I dont have access to every single texture providing website and there are endless possibilities of naming variations. The more people contribute with websites and their naming convention, the better the tool will recognize the texture types.


## 🔮 Future Plans
with plans to expand the script to support materials for **Redshift**, **Arnold**, **Vray** and more.


## ❤️ Support
If you find this Houdini script useful and would like to support its continued development as well as that of other tools, there are several ways you can show your appreciation:
### Buy Me a Coffee
Your support helps fuel late-night coding sessions and keeps the creativity flowing! [You can donate here.](https://www.paypal.com/donate/?hosted_button_id=Z8ER4W6ZMXTCC)
### Connect on Social Media
Follow me on social media to stay updated on the latest developments and memes. Your engagement and feedback are invaluable.
   - [Linkedin](https://www.linkedin.com/in/ccnst/) 
   - [Twitter](https://twitter.com/ccornesteanu)
   - [Artstation](https://www.artstation.com/ccornesteanu) 
### Share Your Experience
   I'd love to hear how you are using the tool in your projects. Send me a message sharing your experiences, challenges, or success stories. Your insights can help shape future improvements.
   Feel free to reach out via Email or through the GitHub Issues page.
   
   Your support, whether through a small donation or a simple message, goes a long way in motivating me to enhance and maintain this tool for the community. Thank you for being a part of this journey!

