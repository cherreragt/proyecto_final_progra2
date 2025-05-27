import sys
import matplotlib.pyplot as plt
import networkx as nx
import csv
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QFileDialog

DB_HOST = 'localhost'
DB_USER = 'user1'
DB_PASSWORD = 'root1'
DB_NAME = 'grafo_guatemala'

class GrafoMunicipios:
    def __init__(self):
        self.grafo = {}

    def agregar_municipio(self, municipio):
        if municipio not in self.grafo:
            self.grafo[municipio] = []

    def agregar_conexion(self, origen, destino, distancia):
        if origen in self.grafo and destino in self.grafo:
            self.grafo[origen].append((destino, distancia))
            self.grafo[destino].append((origen, distancia))

    def cargar_desde_db(self):
        conexion = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cursor = conexion.cursor()
        cursor.execute("SELECT origen, destino, distancia FROM grafo_municipios")
        for origen, destino, distancia in cursor.fetchall():
            self.agregar_municipio(origen)
            self.agregar_municipio(destino)
            self.agregar_conexion(origen, destino, distancia)
        conexion.close()

    def guardar_en_db(self, origen, destino, distancia):
        conexion = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO grafo_municipios (origen, destino, distancia) VALUES (%s, %s, %s)",
                       (origen, destino, distancia))
        conexion.commit()
        conexion.close()

    def mostrar_grafo(self):
        print("Grafo de municipios:")
        for municipio, conexiones in self.grafo.items():
            print(f"{municipio}: {conexiones}")

    def bfs(self, inicio):
        visitados = []
        cola = [inicio]
        orden = []  # Para registrar el orden de recorrido

        while cola:
            nodo = cola.pop(0)
            if nodo not in visitados:
                visitados.append(nodo)
                orden.append(nodo)  # Guardamos el orden
                for vecino, _ in self.grafo.get(nodo, []):
                    if vecino not in visitados:
                        cola.append(vecino)
        return orden

    def dfs(self, inicio, visitados=None, orden=None):
        if visitados is None:
            visitados = []
        if orden is None:
            orden = []

        visitados.append(inicio)
        orden.append(inicio)  # Guardamos el orden
        for vecino, _ in self.grafo.get(inicio, []):
            if vecino not in visitados:
                self.dfs(vecino, visitados, orden)

        return orden

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.grafo = GrafoMunicipios()
        self.grafo.cargar_desde_db()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Grafo de Municipios de Guatemala")
        layout = QVBoxLayout()

        self.label = QLabel("Visualización del Grafo")
        layout.addWidget(self.label)

        self.input_origen = QLineEdit()
        self.input_origen.setPlaceholderText("Origen")

        self.input_destino = QLineEdit()
        self.input_destino.setPlaceholderText("Destino")

        self.input_distancia = QLineEdit()
        self.input_distancia.setPlaceholderText("Distancia (km)")

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.input_origen)
        form_layout.addWidget(self.input_destino)
        form_layout.addWidget(self.input_distancia)

        btn_agregar_conexion = QPushButton("Agregar Conexión")
        btn_agregar_conexion.clicked.connect(self.agregar_conexion)

        layout.addLayout(form_layout)
        layout.addWidget(btn_agregar_conexion)

        btn_ver = QPushButton("Ver Grafo")
        btn_ver.clicked.connect(self.ver_grafo)
        layout.addWidget(btn_ver)

        self.input_inicio = QLineEdit()
        self.input_inicio.setPlaceholderText("Municipio de inicio")
        layout.addWidget(self.input_inicio)

        btn_bfs = QPushButton("Recorrido BFS")
        btn_bfs.clicked.connect(self.mostrar_bfs)
        layout.addWidget(btn_bfs)

        btn_dfs = QPushButton("Recorrido DFS")
        btn_dfs.clicked.connect(self.mostrar_dfs)
        layout.addWidget(btn_dfs)

        btn_cargar_csv = QPushButton("Cargar CSV")
        btn_cargar_csv.clicked.connect(self.cargar_csv)
        layout.addWidget(btn_cargar_csv)

        self.setLayout(layout)

    def agregar_conexion(self):
        origen = self.input_origen.text()
        destino = self.input_destino.text()
        distancia = self.input_distancia.text()

        if origen and destino and distancia.isdigit():
            self.grafo.agregar_municipio(origen)
            self.grafo.agregar_municipio(destino)
            self.grafo.agregar_conexion(origen, destino, int(distancia))
            self.grafo.guardar_en_db(origen, destino, int(distancia))
            self.label.setText(f"Conexión agregada: {origen} - {destino} ({distancia} km)")
        else:
            self.label.setText("Entrada inválida. Asegúrate de ingresar origen, destino y distancia.")

    def ver_grafo(self, recorrido=None):
        G = nx.Graph()
        for municipio, conexiones in self.grafo.grafo.items():
            G.add_node(municipio)
            for destino, distancia in conexiones:
                G.add_edge(municipio, destino, weight=distancia)

        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        if recorrido:
            path_edges = [(recorrido[i], recorrido[i+1]) for i in range(len(recorrido)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2)

        plt.show()

    def mostrar_bfs(self):
        inicio = self.input_inicio.text()
        if inicio and inicio in self.grafo.grafo:
            recorrido = self.grafo.bfs(inicio)
            self.ver_grafo(recorrido)
            recorrido_texto = ' -> '.join(f'{i+1}. {municipio}' for i, municipio in enumerate(recorrido))
            self.label.setWordWrap(True)
            self.label.setText(f"Recorrido BFS desde {inicio}: {recorrido_texto}")
        else:
            self.label.setText("Municipio no válido para BFS.")

    def mostrar_dfs(self):
        inicio = self.input_inicio.text()
        if inicio and inicio in self.grafo.grafo:
            recorrido = self.grafo.dfs(inicio)
            self.ver_grafo(recorrido)
            recorrido_texto = ' -> '.join(f'{i+1}. {municipio}' for i, municipio in enumerate(recorrido))
            self.label.setWordWrap(True)
            self.label.setText(f"Recorrido DFS desde {inicio}: {recorrido_texto}")
        else:
            self.label.setText("Municipio no válido para DFS.")

    def cargar_csv(self):
        # Abrir un cuadro de diálogo para seleccionar el archivo CSV
        archivo, _ = QFileDialog.getOpenFileName(self, "Cargar archivo CSV", "", "Archivos CSV (*.csv)")

        if archivo:
            with open(archivo, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Saltar la cabecera
                for fila in reader:
                    if len(fila) == 3:
                        origen, destino, distancia = fila
                        if distancia.isdigit():
                            self.grafo.agregar_municipio(origen)
                            self.grafo.agregar_municipio(destino)
                            self.grafo.agregar_conexion(origen, destino, int(distancia))
                            self.grafo.guardar_en_db(origen, destino, int(distancia))
            self.label.setText(f"Archivo CSV cargado: {archivo}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
