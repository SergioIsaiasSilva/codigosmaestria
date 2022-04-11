# codigosmaestria
Se agregan los codigos empleados en la generación de resultados para el modelo de optimización


Instrucciones para la instalación.
a)	Instalar Python. Para esta implementación se usa Python 3.9.5
b)	Instalar GAMS. Tenerlo con licencia vigente.
c)	Ejecutar las siguientes instrucciones como administrador en el símbolo de sistema. Colocar USUARIO y RUTA DE INSTALACIÓN DE GAMS que corresponde en su caso.

curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
set PYTHONPATH=C:\”RUTA DE INSTALACIÓN DE GAMS”\apifiles\Python\api_39
set PYTHONPATH=C:\”RUTA DE INSTALACIÓN DE GAMS”\apifiles\Python\gams;%PYTHONPATH%
cd C:\”RUTA DE INSTALACIÓN DE GAMS”\apifiles\Python\api_39
C:\Users\”USUARIO”\AppData\Local\Programs\Python\Python39\python.exe setup.py install
C:\Users\”USUARIO”\AppData\Local\Programs\Python\Python39\python.exe C:\”RUTA DE INSTALACIÓN DE GAMS”\apifiles\Python\transport1.py
pip install numpy
pip install tabulate
pip install PySimpleGUI
pip install openpyxl
pip install matplotlib

Recomendable hacer línea por línea, para evitar problemas.
La primer línea permite instalar un instalador de librerías a Python de forma simple.
En la segunda y tercera línea se establece una ruta PATH, para que Python reconozca a GAMS y sus archivos al llamarlo en CMD.
En la cuarta y quinta línea se ejecuta el instalador del API de GAMS para poder se llamado desde Python.
Para la sexta línea se hace una prueba, consiste en abrir un archivo ejemplo de GAMS desde Python. Al ejecutarse inmediatamente arroja los siguientes resultados.

Copy ASCII : trnsport.gms
Ran with Default:
x(seattle,new-york): level=50.0 marginal=0.0
x(seattle,chicago): level=300.0 marginal=0.0
x(seattle,topeka): level=0.0 marginal=0.036000000000000004
x(san-diego,new-york): level=275.0 marginal=0.0
x(san-diego,chicago): level=0.0 marginal=0.009000000000000008
x(san-diego,topeka): level=275.0 marginal=0.0
Ran with XPRESS:
x(seattle,new-york): level=0.0 marginal=5e-324
x(seattle,chicago): level=300.0 marginal=0.0
x(seattle,topeka): level=0.0 marginal=0.036000000000000004
x(san-diego,new-york): level=325.0 marginal=0.0
x(san-diego,chicago): level=0.0 marginal=0.009000000000000008
x(san-diego,topeka): level=275.0 marginal=0.0
Ran with XPRESS with non-default option:
x(seattle,new-york): level=50.0 marginal=0.0
x(seattle,chicago): level=300.0 marginal=0.0
x(seattle,topeka): level=0.0 marginal=0.036000000000000004
x(san-diego,new-york): level=275.0 marginal=0.0
x(san-diego,chicago): level=0.0 marginal=0.009000000000000008
x(san-diego,topeka): level=275.0 marginal=0.0



En las últimas líneas se instalan las librerías necesarias para Python, como es la librería para trabajar con arrays, tabulate para generar las tablas, PySimpleGui genera la ventana de interfaz de usuario, con las últimas dos para generar gráficas de forma exitosa.

Al obtener los resultados se puede abrir la implementación computacional de forma segura.



