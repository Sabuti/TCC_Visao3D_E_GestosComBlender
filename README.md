# TCC_Visao3D_E_GestosComBlender
Codes for prototyping a new way to use Blender, using hands, with the help of 3D glasses for better experience

## Necessary Itens
- 3D glasses (red/cyan);
- Notebook capable of running Blender;

## Hardware setup
- Turn on the notebook;
- Open Blender and Visual Studio Code (VS Code);

## Software Setup
- Download and install Python 3.11.x;
- Install pip (most recent version);
- Download and install Blender 4.3.x;
- Download and install VS Code (most recent version);
- Clone repository on VS Code;
- Change interpreter to Python 3.11.x;
- Create enviroment:
``` bash 
python.exe -m venv .venv
```
- Activate enviroment:
``` bash  
.venv\Script\Activate
``` 
- Download and install specific versions of libraries: 
``` bash  
python -m pip install mediapipe==0.10.14 opencv-python==4.9.0.80 numpy==1.26.4
```
## How to run it
* Inside Blender, configure output and camera to use stereoscopy
* Add the tcc_bpy doc in the Script area; and run it to open the server;
* Run the tcc_main doc, in VS Code, to connect as a client and open the camera;
* Put on the 3D glasses and look around the scenes.