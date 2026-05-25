"""
Google Cloud Run - SELECT simple de tabla fondeo_x en Oracle
"""

import json
import cx_Oracle
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# ============================================================================
# CONFIGURACIÓN ORACLE
# ============================================================================

TNS_STRING = """(DESCRIPTION=
  (ADDRESS=(PROTOCOL=TCP)(HOST=10.0.220.181)(PORT=1523))
  (CONNECT_DATA=
    (SERVER=DEDICATED)
    (SERVICE_NAME=PDBBT)
  )
)"""

DB_USER = "DALANOCA_PREBUS"
DB_PASSWORD = "853Ala.@852853"  # CAMBIAR ESTO POR TU PASSWORD REAL

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def ejecutar_select():
    """Conecta a Oracle y hace SELECT de fondeo_x"""
    
    print("="*70)
    print("INICIANDO: SELECT de fondeo_x")
    print("="*70)
    
    try:
        # PASO 1: Conectar a Oracle
        print("\n[PASO 1] Conectando a Oracle...")
        
        try:
            cx_Oracle.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_13")
        except:
            pass
        
        conexion = cx_Oracle.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=TNS_STRING
        )
        
        print("✓ Conexión exitosa")
        
        # PASO 2: Ejecutar SELECT
        print("\n[PASO 2] Ejecutando SELECT...")
        
        cursor = conexion.cursor()
        
        # SELECT simple - primeras 5 filas
        query = """
        SELECT *
        FROM DALANOCA_PREBUS.fondeo_x
        WHERE ROWNUM <= 5
        """
        
        print(f"Query: {query}")
        
        cursor.execute(query)
        
        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]
        print(f"\nColumnas: {columnas}")
        
        # Obtener datos
        datos = cursor.fetchall()
        
        print(f"✓ {len(datos)} registros obtenidos\n")
        
        # Mostrar datos
        print("DATOS:")
        print("-" * 70)
        for i, fila in enumerate(datos, 1):
            print(f"Fila {i}: {fila}")
        print("-" * 70)
        
        cursor.close()
        conexion.close()
        
        print("\n" + "="*70)
        print("✓ QUERY COMPLETADA EXITOSAMENTE")
        print("="*70)
        
        return {
            'statusCode': 200,
            'mensaje': 'Éxito',
            'columnas': columnas,
            'registros': len(datos),
            'datos': [dict(zip(columnas, fila)) for fila in datos]
        }
    
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'error': str(e)
        }

# ============================================================================
# ENDPOINT PARA CLOUD RUN
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def main():
    """Endpoint que Cloud Run llama"""
    resultado = ejecutar_select()
    
    # Imprimir resultado para logs
    print("\nRESULTADO JSON:")
    print(json.dumps(resultado, indent=2, default=str))
    
    return json.dumps(resultado, default=str), resultado['statusCode']

@app.route('/health', methods=['GET'])
def health():
    """Health check para Cloud Run"""
    return json.dumps({'status': 'ok'}), 200

if __name__ == '__main__':
    # Para testing local
    resultado = ejecutar_select()
    print("\n" + "="*70)
    print("RESULTADO FINAL:")
    print(json.dumps(resultado, indent=2, default=str))
