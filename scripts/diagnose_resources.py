#!/usr/bin/env python3
"""
Script de diagnóstico de recursos para procesamiento de PDFs
Diagnóstica los recursos disponibles y recomienda configuración óptima.

Uso:
    python scripts/diagnose_resources.py

O desde Docker:
    docker compose run ingestion python scripts/diagnose_resources.py
"""

import os
import sys
import platform
import shutil

def get_system_resources():
    """Obtener información de recursos del sistema usando métodos nativos"""
    print("🖥️  INFORMACIÓN DEL SISTEMA")
    print("=" * 50)
    
    resources: dict[str, float] = {}
    
    # CPU
    try:
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        print(f"CPUs disponibles: {cpu_count}")
        resources['cpu_count'] = cpu_count
    except:
        print("CPUs disponibles: No se pudo determinar")
        resources['cpu_count'] = 2  # Fallback
    
    # Memoria usando /proc/meminfo (Linux)
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            mem_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    mem_info[key.strip()] = value.strip()
        
        total_kb = int(mem_info['MemTotal'].split()[0])
        available_kb = int(mem_info['MemAvailable'].split()[0])
        
        total_gb = total_kb / (1024**2)
        available_gb = available_kb / (1024**2)
        
        print(f"💾 MEMORIA:")
        print(f"Total: {total_gb:.1f} GB")
        print(f"Disponible: {available_gb:.1f} GB")
        print(f"Usado: {((total_gb - available_gb) / total_gb) * 100:.1f}%")
        
        resources['memory_total_gb'] = total_gb
        resources['memory_available_gb'] = available_gb
        
    except Exception as e:
        print(f"💾 MEMORIA: No se pudo determinar ({e})")
        resources['memory_total_gb'] = 4.0  # Fallback
        resources['memory_available_gb'] = 2.0
    
    # Espacio en disco
    try:
        usage = shutil.disk_usage('/')
        total_gb = usage.total / (1024**3)
        free_gb = usage.free / (1024**3)
        
        print(f"💿 DISCO:")
        print(f"Total: {total_gb:.1f} GB")
        print(f"Libre: {free_gb:.1f} GB")
        print(f"Usado: {((total_gb - free_gb) / total_gb) * 100:.1f}%")
        
        resources['disk_free_gb'] = free_gb
        
    except Exception as e:
        print(f"💿 DISCO: No se pudo determinar ({e})")
        resources['disk_free_gb'] = 10.0  # Fallback
    
    return resources

def get_container_limits():
    """Verificar límites específicos del contenedor Docker"""
    print(f"\n🐳 LÍMITES DEL CONTENEDOR")
    print("=" * 50)
    
    limits = {}
    
    # Verificar si estamos en un contenedor
    in_container = os.path.exists('/.dockerenv')
    if not in_container:
        print("No se detectó entorno Docker - ejecutándose directamente en el host")
        return limits
    
    # Límite de memoria
    memory_files = [
        '/sys/fs/cgroup/memory/memory.limit_in_bytes',
        '/sys/fs/cgroup/memory.max',  # cgroup v2
    ]
    
    for memory_file in memory_files:
        try:
            with open(memory_file, 'r') as f:
                memory_limit = f.read().strip()
                if memory_limit != 'max':
                    memory_limit = int(memory_limit)
                    if memory_limit < (1024**4):  # Si es menor que 1TB, es un límite real
                        memory_limit_gb = memory_limit / (1024**3)
                        print(f"Límite de memoria: {memory_limit_gb:.1f} GB")
                        limits['memory_limit_gb'] = memory_limit_gb
                        break
        except:
            continue
    else:
        print("Límite de memoria: Sin límite específico")
        limits['memory_limit_gb'] = None
    
    # Límite de CPU
    cpu_files = [
        ('/sys/fs/cgroup/cpu/cpu.cfs_quota_us', '/sys/fs/cgroup/cpu/cpu.cfs_period_us'),
        ('/sys/fs/cgroup/cpu.max', None),  # cgroup v2
    ]
    
    for quota_file, period_file in cpu_files:
        try:
            with open(quota_file, 'r') as f:
                content = f.read().strip()
                
            if period_file:  # cgroup v1
                if content != '-1':
                    cpu_quota = int(content)
                    with open(period_file, 'r') as f:
                        cpu_period = int(f.read().strip())
                    cpu_limit = cpu_quota / cpu_period
                    print(f"Límite de CPU: {cpu_limit:.2f} cores")
                    limits['cpu_limit'] = cpu_limit
                    break
            else:  # cgroup v2
                if content != 'max':
                    parts = content.split()
                    if len(parts) == 2:
                        cpu_quota, cpu_period = map(int, parts)
                        cpu_limit = cpu_quota / cpu_period
                        print(f"Límite de CPU: {cpu_limit:.2f} cores")
                        limits['cpu_limit'] = cpu_limit
                        break
        except:
            continue
    else:
        print("Límite de CPU: Sin límite específico")
        limits['cpu_limit'] = None
    
    return limits

def recommend_pdf_processing_settings(resources, limits):
    """Recomendar configuración específica para procesamiento de PDFs"""
    print(f"\n🎯 RECOMENDACIONES PARA PROCESAMIENTO DE PDFs")
    print("=" * 60)
    
    # Determinar CPUs efectivos
    available_cpus = resources['cpu_count']
    if limits.get('cpu_limit'):
        available_cpus = min(available_cpus, int(limits['cpu_limit']))
    
    # Configuración conservadora: dejar al menos 1 CPU libre
    recommended_workers = max(2, min(available_cpus - 1, 10))
    
    # Determinar memoria efectiva
    available_memory = resources['memory_available_gb']
    if limits.get('memory_limit_gb'):
        available_memory = min(available_memory, limits['memory_limit_gb'] * 0.9)  # 90% del límite
    
    # Estimar memoria por PDF (conservador: ~100MB por PDF incluyendo embeddings)
    memory_per_pdf_gb = 0.1
    safe_batch_size = max(5, int(available_memory * 0.6 / memory_per_pdf_gb))
    safe_batch_size = min(safe_batch_size, 100)  # Máximo razonable
    
    print(f"Recursos detectados:")
    print(f"  • CPUs efectivos: {available_cpus}")
    print(f"  • Memoria efectiva: {available_memory:.1f} GB")
    print(f"  • Espacio libre: {resources['disk_free_gb']:.1f} GB")
    
    print(f"\nConfiguración recomendada:")
    print(f"  • max_workers: {recommended_workers}")
    print(f"  • batch_size: {safe_batch_size}")
    
    # Advertencias y consejos
    print(f"\n⚠️  CONSIDERACIONES:")
    
    if available_memory < 4:
        print("  • MEMORIA BAJA: Considera reducir batch_size a 10-20")
        safe_batch_size = min(safe_batch_size, 20)
    
    if available_cpus <= 2:
        print("  • CPU LIMITADO: El procesamiento será lento")
        recommended_workers = 2
    
    if resources['disk_free_gb'] < 5:
        print("  • POCO ESPACIO: Monitorea el uso de disco durante el proceso")
    
    if available_memory > 16:
        print("  • MEMORIA ABUNDANTE: Puedes aumentar batch_size para mejor rendimiento")
        safe_batch_size = min(safe_batch_size * 2, 200)
    
    # Configuración final
    print(f"\n📋 CÓDIGO SUGERIDO PARA main():")
    print(f"```python")
    print(f"all_docs = process_pdfs_in_parallel(")
    print(f"    pdf_keys,")
    print(f"    max_workers={recommended_workers},  # Hilos concurrentes")
    print(f"    batch_size={safe_batch_size}       # PDFs por lote")
    print(f")")
    print(f"```")
    
    # Estimación de tiempo
    estimated_time_per_pdf = 3  # segundos promedio por PDF
    total_time_sequential = len(sys.argv) > 1 and sys.argv[1].isdigit() and int(sys.argv[1]) * estimated_time_per_pdf or 0
    if total_time_sequential > 0:
        total_pdfs = int(sys.argv[1])
        parallel_time = (total_pdfs * estimated_time_per_pdf) / recommended_workers
        
        print(f"\n⏱️  ESTIMACIÓN DE TIEMPO (para {total_pdfs:,} PDFs):")
        print(f"  • Secuencial: ~{total_time_sequential/3600:.1f} horas")
        print(f"  • Paralelo: ~{parallel_time/3600:.1f} horas")
        print(f"  • Mejora: {total_time_sequential/parallel_time:.1f}x más rápido")

def main():
    print("🔍 DIAGNÓSTICO DE RECURSOS - PROCESAMIENTO DE PDFs")
    print("=" * 70)
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("\nUso:")
        print("  python scripts/diagnose_resources.py [numero_pdfs]")
        print("\nEjemplo:")
        print("  python scripts/diagnose_resources.py 10000")
        return
    
    try:
        resources = get_system_resources()
        limits = get_container_limits()
        recommend_pdf_processing_settings(resources, limits)
        
        print(f"\n💡 CONSEJOS ADICIONALES:")
        print(f"  • Ejecuta 'docker stats' durante el procesamiento para monitorear")
        print(f"  • Si hay errores de memoria, reduce batch_size")
        print(f"  • Si hay errores de timeout, reduce max_workers")
        print(f"  • Guarda logs del proceso para análisis posterior")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        print("Esto puede indicar limitaciones en el entorno actual.")

if __name__ == "__main__":
    main()