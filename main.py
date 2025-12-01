import os
import json
import uuid
import redis
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class GestorKeyDB:
    def __init__(self):
        # Configuración de conexión
        host = os.getenv('KEYDB_HOST', 'localhost')
        port = int(os.getenv('KEYDB_PORT', 6379))
        password = os.getenv('KEYDB_PASSWORD', None)

        try:
            # decode_responses=True hace que redis nos devuelva Strings en vez de Bytes
            self.db = redis.Redis(
                host=host,
                port=port,
                password=password,
                decode_responses=True
            )
            # Ping para verificar conexión
            self.db.ping()
            print("⚡ Conectado a KeyDB (memoria) exitosamente.")
        except redis.ConnectionError as e:
            print(f"❌ Error conectando a KeyDB: {e}")
            print("Asegúrate de que el servidor esté corriendo.")
            exit()

    def agregar_libro(self, titulo, autor, genero, estado):
        # 1. Generar un ID único
        book_id = str(uuid.uuid4())
        key = f"libro:{book_id}"  # Prefijo para organizar claves

        # 2. Crear diccionario
        libro_dict = {
            "id": book_id,
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado
        }

        # 3. Serializar a JSON y guardar (SET)
        try:
            val_json = json.dumps(libro_dict)
            self.db.set(key, val_json)
            return True
        except Exception as e:
            print(f"Error guardando: {e}")
            return False

    def listar_libros(self):
        libros = []
        # SCAN es más seguro que KEYS en producción porque no bloquea el servidor
        # Buscamos todas las claves que empiecen con "libro:"
        for key in self.db.scan_iter("libro:*"):
            val_json = self.db.get(key)
            if val_json:
                libros.append(json.loads(val_json))
        return libros

    def buscar_libros(self, termino):
        # KeyDB no es un motor de búsqueda de texto nativo (como Mongo o SQL).
        # Estrategia: Traer todo y filtrar en Python (OK para proyectos pequeños)
        todos = self.listar_libros()
        termino = termino.lower()

        resultados = [
            l for l in todos
            if termino in l['titulo'].lower() or
               termino in l['autor'].lower() or
               termino in l['genero'].lower()
        ]
        return resultados

    def actualizar_libro(self, id_libro, nuevos_datos):
        key = f"libro:{id_libro}"

        # 1. Verificar si existe
        if not self.db.exists(key):
            return False

        try:
            # 2. Obtener dato actual (GET)
            val_json = self.db.get(key)
            libro_actual = json.loads(val_json)

            # 3. Actualizar campos (limpiamos vacíos)
            for k, v in nuevos_datos.items():
                if v:  # Si el usuario escribió algo
                    libro_actual[k] = v

            # 4. Guardar de nuevo (SET - Sobreescribe)
            self.db.set(key, json.dumps(libro_actual))
            return True
        except Exception as e:
            print(f"Error actualizando: {e}")
            return False

    def eliminar_libro(self, id_libro):
        key = f"libro:{id_libro}"
        # DEL retorna el número de claves eliminadas
        resultado = self.db.delete(key)
        return resultado > 0


# --- INTERFAZ (UI) ---

def mostrar_tabla(libros):
    if not libros:
        print("\n(Base de datos vacía o sin resultados)")
        return

    print("\n" + "=" * 100)
    print(f"{'ID (UUID)':<37} | {'TÍTULO':<20} | {'AUTOR':<20} | {'ESTADO':<10}")
    print("-" * 100)
    for l in libros:
        print(f"{l['id']:<37} | {l['titulo']:<20} | {l['autor']:<20} | {l['estado']:<10}")
    print("=" * 100 + "\n")


def menu():
    gestor = GestorKeyDB()

    while True:
        print("\n--- ⚡ TURBO-LIBRARIAN (KeyDB/Redis) ---")
        print("1. Agregar libro")
        print("2. Ver catálogo")
        print("3. Buscar")
        print("4. Editar")
        print("5. Borrar")
        print("6. Salir")

        op = input("\nOpción: ")

        if op == '1':
            t = input("Título: ")
            a = input("Autor: ")
            g = input("Género: ")
            e = "Leído" if input("¿Leído? (s/n): ").lower() == 's' else "No leído"
            if gestor.agregar_libro(t, a, g, e): print("✅ Guardado en memoria.")

        elif op == '2':
            mostrar_tabla(gestor.listar_libros())

        elif op == '3':
            q = input("Buscar: ")
            mostrar_tabla(gestor.buscar_libros(q))

        elif op == '4':
            mostrar_tabla(gestor.listar_libros())
            uid = input("ID a editar (copiar/pegar): ").strip()
            print("(Enter para mantener actual)")
            cambios = {
                "titulo": input("Nuevo Título: "),
                "autor": input("Nuevo Autor: "),
                "genero": input("Nuevo Género: "),
                "estado": ""
            }
            e_in = input("Nuevo Estado (s/n): ").lower()
            if e_in == 's':
                cambios["estado"] = "Leído"
            elif e_in == 'n':
                cambios["estado"] = "No leído"

            if gestor.actualizar_libro(uid, cambios):
                print("✅ Actualizado.")
            else:
                print("❌ Error o ID no existe.")

        elif op == '5':
            uid = input("ID a borrar: ").strip()
            if gestor.eliminar_libro(uid):
                print("🗑️ Eliminado.")
            else:
                print("❌ No encontrado.")

        elif op == '6':
            break


if __name__ == "__main__":
    menu()