# TCC_Visao3D_E_GestosComBlender
Codes for prototyping a new way to use Blender, using hands, and with the help of 3D glasses

## Necessary Itens
- 3D glasses (red/cyan);
- Powerful notebook to run Blender;
- Projector;
- HDMI cable;

## Hardware setup
- Turn on the projector;
- Turn on the notebook;
- Connect the projector to the notebook;

## Software Setup
- Download and install Python 3.11.x
- Install pip (most recent version)
- Download and install Blender ?x?
- Clone repository
- Change interpreter to Python 3.11.x
- Create enviroment; (??)  
``` bash 
python.exe -m venv .venv
```
- Activate enviroment; 
``` bash  
.venv\Script\Activate
``` 
- Download and install specific versions of used libraries 
``` bash  
python -m pip install mediapipe==0.10.14 opencv-python==4.9.0.80 numpy==1.26.4
```
## How to run it
* Open Blender and add the tcc_bpy.py in the Script area;
* Run the script inside Blender, to open the server;
* Run the tcc_main to connect as a client and inicialize(?) the camera;
* Put on the 3D glasses and enjoy it.