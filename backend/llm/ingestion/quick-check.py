#!/usr/bin/env python3
"""
Script de verificación rápida para ChromaDB
Uso: python quick_check.py
"""

import os
import sys
import chromadb

def quick_check():
    VECTOR_DIR = "/app/vector-store"  # Ajusta tu ruta
    
    print("🔍 VERIFICACIÓN RÁPIDA DE CHROMADB")
    print("=" * 40)
    
    # Verificar si existe el directorio
    if not os.path.exists(VECTOR_DIR):
        print(f"❌ El directorio {VECTOR_DIR} no existe")
        return
    
    # Listar archivos
    files = os.listdir(VECTOR_DIR)
    print(f"📁 Archivos encontrados: {len(files)}")
    for file in files[:10]:  # Mostrar solo los primeros 10
        print(f"  - {file}")
    
    if len(files) > 10:
        print(f"  ... y {len(files) - 10} más")
    
    # Conectar a ChromaDB
    try:
        client = chromadb.PersistentClient(path=VECTOR_DIR)
        collections = client.list_collections()
        
        print(f"\n📦 Colecciones: {len(collections)}")
        
        total_docs = 0
        for collection in collections:
            count = collection.count()
            total_docs += count
            print(f"  - {collection.name}: {count:,} documentos")
        
        print(f"\n📊 TOTAL DE DOCUMENTOS: {total_docs:,}")
        
        # Si hay documentos, mostrar un ejemplo
        if total_docs > 0:
            collection = collections[0]  # Tomar la primera colección
            sample = collection.get(limit=1, include=['documents', 'metadatas'])
            
            print(f"\n📄 EJEMPLO DE DOCUMENTO:")
            if sample['documents']:
                doc = sample['documents'][0]
                print(f"  Contenido: {doc[:200]}...")
            
            if sample['metadatas'] and sample['metadatas'][0]:
                print(f"  Metadata: {sample['metadatas'][0]}")
    
    except Exception as e:
        print(f"❌ Error accediendo a ChromaDB: {e}")

if __name__ == "__main__":
    quick_check()