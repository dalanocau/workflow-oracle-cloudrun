"""
Google Cloud Run - SELECT simple de tabla fondeo_x en Oracle
"""

import json
import os
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    logger.info("="*70)
    logger.info("INICIANDO: SELECT de fondeo_x")
    logger.info("="*70)
    
    try:
        # IMPORTAR AQUÍ para no fallar al iniciar
        import oracledb
        
        # PASO 1: Conectar a Oracle
        logger.info("[PASO 1] Conectando a Oracle...")
        
        try:
            oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_13")
            logger.info("Oracle Client inicializado")
        except Exception as e:
            logger.info(f"Oracle Client no necesario: {e}")
        
        conexion = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=TNS_STRING,
            thick_mode=False  # Thin mode (no necesita Oracle Client)
        )
        
        logger.info("✓ Conexión exitosa")
        
        # PASO 2: Ejecutar SELECT
        logger.info("[PASO 2] Ejecutando SELECT...")
        
        cursor = conexion.cursor()
        
        # SELECT simple - primeras 5 filas
        query = """
        SELECT *
        FROM DALANOCA_PREBUS.fondeo_x
        WHERE ROWNUM <= 5
        """
        
        logger.info(f"Query: {query}")
        
        cursor.execute(query)
        
        # Obtener nombres de columnas
        columnas = [desc[0] for desc in cursor.description]
        logger.info(f"Columnas: {columnas}")
        
        # Obtener datos
        datos = cursor.fetchall()
        
        logger.info(f"✓ {len(datos)} registros obtenidos")
        
        # Mostrar datos
        logger.info("DATOS:")
        logger.info("-" * 70)
        for i, fila in enumerate(datos, 1):
            logger.info(f"Fila {i}: {fila}")
        logger.info("-" * 70)
        
        cursor.close()
        conexion.close()
        
        logger.info("="*70)
        logger.info("✓ QUERY COMPLETADA EXITOSAMENTE")
        logger.info("="*70)
        
        return {
            'statusCode': 200,
            'mensaje': 'Éxito',
            'columnas': columnas,
            'registros': len(datos),
            'datos': [list(fila) for fila in datos]
        }
    
    except Exception as e:
        logger.error(f"✗ ERROR: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            'statusCode': 500,
            'error': str(e),
            'tipo': type(e).__name__
        }

# ============================================================================
# ENDPOINTS PARA CLOUD RUN
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def main():
    """Endpoint que Cloud Run llama"""
    logger.info("Recibida solicitud en /")
    resultado = ejecutar_select()
    
    logger.info("RESULTADO JSON:")
    logger.info(json.dumps(resultado, indent=2, default=str))
    
    return json.dumps(resultado, default=str), resultado['statusCode']

@app.route('/health', methods=['GET'])
def health():
    """Health check para Cloud Run - IMPORTANTE para el inicio"""
    logger.info("Health check OK")
    return json.dumps({'status': 'ok', 'healthy': True}), 200

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    logger.info("Test endpoint llamado")
    return json.dumps({'message': 'Cloud Run está corriendo'}), 200

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Iniciando Flask en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
