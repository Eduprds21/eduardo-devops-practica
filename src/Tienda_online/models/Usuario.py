"""
Módulo Usuario
Define la clase base Usuario y sus subclases especializadas Cliente y Administrador.
"""

import uuid


class Usuario:
    """
    Clase padre que representa a cualquier usuario que interactúa con la tienda.
    
    Atributos:
        id (str): Identificador único generado automáticamente.
        nombre (str): Nombre completo del usuario.
        email (str): Correo electrónico del usuario.
    """

    def __init__(self, nombre: str, email: str, id_usuario: str | None = None) -> None:
        """
        Inicializa un nuevo usuario con sus datos básicos y un ID único.
        """
        self.id: str = id_usuario if id_usuario else str(uuid.uuid4())[:8]
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """
        Indica si el usuario tiene permisos de administrador.
        Por defecto, cualquier usuario base no es administrador (devuelve False).
        """
        return False

    def __str__(self) -> str:
        """
        Devuelve una representación en texto del usuario.
        """
        return f"[ID: {self.id}] {self.nombre} ({self.email})"


class Cliente(Usuario):
    """
    Subclase de Usuario que representa a los clientes compradores de la tienda.
    
    Atributos adicionales:
        direccion (str): Dirección postal para los envíos de pedidos.
    """

    def __init__(self, nombre: str, email: str, direccion: str, id_usuario: str | None = None) -> None:
        """
        Inicializa un cliente con sus datos personales y dirección de envío.
        """
        super().__init__(nombre, email, id_usuario)
        self.direccion: str = direccion

    def __str__(self) -> str:
        """
        Representación legible del cliente con su dirección postal.
        """
        return (
            f"[ID: {self.id}] Cliente: {self.nombre} | "
            f"Email: {self.email} | "
            f"Dirección: {self.direccion}"
        )


class Administrador(Usuario):
    """
    Subclase de Usuario que representa al personal gestor y administrador de la tienda.
    """

    def __init__(self, nombre: str, email: str, id_usuario: str | None = None) -> None:
        """
        Inicializa un administrador del sistema.
        """
        super().__init__(nombre, email, id_usuario)

    def is_admin(self) -> bool:
        """
        Sobrescribe el método base para reflejar los privilegios de administrador (devuelve True).
        """
        return True

    def __str__(self) -> str:
        """
        Representación legible del administrador.
        """
        return f"[ID: {self.id}] Administrador: {self.nombre} | Email: {self.email}"
