# 🤝 Contributing
## Foreword
This chapter serves as a guide for extending the script to meet your individual needs. Due to my other commitments, I won't be able to consistently add support for new renderers or texture types on a frequent basis. This is why I've designed the tool to be easily expandable, allowing anyone with some Python knowledge to incorporate support for their preferred texture providers or more niche texture types. If you choose to enhance the script in this manner, contributing to the GitHub repository would be highly valued, enabling everyone to benefit from open-source collaboration.


> _🚨 Disclaimer 🚨_ Just a heads up: this is my first attempt at a substantial script, and my programming knowledge is self-taught. While the tool does its job quite well, I can't promise that contributing will be a walk in the park. Things might not be as straightforward or intuitive; your patience and understanding are greatly appreciated!


## Adding missing texture names
This is something everyone can do with minimal Python or scripting knowledge. Just follow the already existing structure inside the variable `supportedTextures_data` and add your own name variations. 

I don't have access to every single texture providing website (nor the patience to do so), and since every website has its own naming conventions, there seem to be endless possibilities for naming variations. The more people contribute with their naming variations, the better the tool will be at recognizing every file name from every website.

## Adding missing texture types
   1. Add the name of the texture type inside `supportedTextures_data`.
   2. Add your new naming variations following the same conventions as the other texture types above.
   3. Now you need to make the actual code for the node creation inside `def nodeCreation()`. Again it's best to look at how the other texture nodes are being created and connected to other nodes. The most important variables will be:
      - set: The name of the texture set, e.g. For a file named `myTextures_4k_normal.png`, the set_name would be `myTextures_4k`.
      - goalNode: This is the network where the nodes will be created.
      - file_data: This is a variable that holds the data of each selected file. Things like the path to the file, the file name, the file extension and the recognized texture type. The data would first need to be unpacked, but again, it makes sense to look at how it has been done for the other renderers. I normally did it like this:
      ```
        for metadata in file_data:
            file_path,file_name,texture_type,texture_set,file_extension = metadata    
      ```

## Adding render engines
   1. Add the name of the new render engine to `supported_renderers`.
   2. Now you just have to handle the actual node creation inside `def nodeCreation()`. See step 3. above in [Adding missing texture types](#adding-missing-texture-types). The only difference being, that you will need to create the whole material from the ground up.
