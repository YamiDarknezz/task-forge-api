import os
from app import create_app, db

# Create Flask application
app = create_app()


@app.cli.command()
def init_db():
    """Inicializar la base de datos"""
    db.create_all()
    print('Base de datos inicializada con exito!')


@app.cli.command()
def drop_db():
    """Eliminar todas las tablas de la base de datos"""
    if input('Estas seguro de que quieres eliminar todas las tablas? (yes/no): ') == 'yes':
        db.drop_all()
        print('Base de datos eliminada con exito!')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
