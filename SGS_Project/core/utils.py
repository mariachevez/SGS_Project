"""
Script independiente para poblar Países, Provincias y Cantones en la Base de Datos.
Ejecución en consola: python poblar_lugares.py
"""

import os
import django
import requests
from pathlib import Path

import sys
import os

# Obtener la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# 1. Configurar y levantar el entorno de Django manualmente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SGS_Project.settings")
django.setup()

# 2. Importaciones de Django y modelos locales (Seguras después de django.setup())
from django.db import transaction
from core.models import Canton, Pais, Provincia


def poblar_todos_los_paises():
    print("--- 1. Obteniendo lista global de países y prefijos ---")
    url_paises = "https://countriesnow.space/api/v0.1/countries"
    url_prefijos = "https://countriesnow.space/api/v0.1/countries/codes"

    try:
        response_paises = requests.get(url_paises)
        response_prefijos = requests.get(url_prefijos)

        if response_paises.status_code != 200 or response_prefijos.status_code != 200:
            print("Error al conectar con los endpoints de la API.")
            return

        lista_paises = response_paises.json().get('data', [])
        lista_prefijos = response_prefijos.json().get('data', [])

        dict_prefijos = {item.get('name'): item.get('dial_code') for item in lista_prefijos if
                         item.get('name') and item.get('dial_code')}

        print(f"Se encontraron {len(lista_paises)} países disponibles en la API.")
        print("--- 2. Guardando países en la Base de Datos ---")

        contador_creados = 0
        contador_existentes = 0

        with transaction.atomic():
            for item in lista_paises:
                nombre_pais_api = item.get('country')
                if not nombre_pais_api:
                    continue

                prefijo_api = dict_prefijos.get(nombre_pais_api, None)
                pais_obj, creado = Pais.objects.get_or_create(
                    nombre=nombre_pais_api.strip(),
                    defaults={'prefijo': prefijo_api}
                )
                if creado:
                    contador_creados += 1
                else:
                    contador_existentes += 1

        print(f"\n¡Proceso Completado con éxito!")
        print(f"Países nuevos creados: {contador_creados}")
        print(f"Países que ya existían: {contador_existentes}")

    except Exception as e:
        print(f"Ocurrió un error al poblar los países: {e}")


def poblar_provincias_y_cantones_prioritarios():
    paises_prioritarios = {
        "ECUADOR": "Ecuador", "COLOMBIA": "Colombia", "PERU": "Peru",
        "ARGENTINA": "Argentina", "BRAZIL": "Brazil", "CHILE": "Chile",
        "VENEZUELA": "Venezuela", "BOLIVIA": "Bolivia", "PARAGUAY": "Paraguay",
        "URUGUAY": "Uruguay", "SPAIN": "Spain", "ITALY": "Italy", "FRANCE": "France",
        "GERMANY": "Germany", "CHINA": "China", "MEXICO": "Mexico", "UNITED STATES": "United States",
        "ENGLAND": "England", "RUSSIA": "Russia", "JAPAN": "Japan"
    }

    print(f"--- Iniciando carga masiva para {len(paises_prioritarios)} países prioritarios ---")
    url_provincias = "https://countriesnow.space/api/v0.1/countries/states"
    url_cantones = "https://countriesnow.space/api/v0.1/countries/state/cities"

    for nombre_db, nombre_api in paises_prioritarios.items():
        try:
            pais_obj, _ = Pais.objects.get_or_create(nombre=nombre_db, defaults={'prefijo': None})
            print(f"\n🌍 [País] Procesando: {pais_obj.nombre}...")

            res_prov = requests.post(url_provincias, json={"country": nombre_api})
            if res_prov.status_code != 200:
                continue

            provincias_api = res_prov.json().get('data', {}).get('states', [])

            with transaction.atomic():
                for prov in provincias_api:
                    nombre_provincia_api = prov.get('name')
                    if not nombre_provincia_api:
                        continue

                    nombre_provincia_db = nombre_provincia_api.strip().upper().replace(" PROVINCE", "").replace(
                        " STATE", "").replace(" DEPARTMENT", "").strip()

                    provincia_obj, _ = Provincia.objects.get_or_create(pais=pais_obj, nombre=nombre_provincia_db)

                    res_cant = requests.post(url_cantones, json={"country": nombre_api, "state": nombre_provincia_api})
                    if res_cant.status_code == 200:
                        cantones_api = res_cant.json().get('data', [])
                        cantones_a_crear = []

                        for canton_name in cantones_api:
                            nombre_canton_db = canton_name.strip().upper()
                            if not Canton.objects.filter(provincia=provincia_obj, nombre=nombre_canton_db).exists():
                                cantones_a_crear.append(Canton(provincia=provincia_obj, nombre=nombre_canton_db))

                        if cantones_a_crear:
                            Canton.objects.bulk_create(cantones_a_crear)

        except Exception as ex:
            print(f"💥 Error procesando {nombre_api}: {ex}")

    print("\n🚀 --- Sincronización masiva completada ---")


# ==========================================
# Ejecutor del Script
# ==========================================
if __name__ == "__main__":
    print("¿Qué deseas hacer?")
    print("1. Poblar Países")
    print("2. Poblar Provincias y Cantones Prioritarios")
    opcion = input("Selecciona una opción (1 o 2): ")

    if opcion == "1":
        poblar_todos_los_paises()
    elif opcion == "2":
        poblar_provincias_y_cantones_prioritarios()
    else:
        print("Opción inválida.")