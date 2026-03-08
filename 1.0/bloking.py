bl_info = {
    "name": "Bloking",
    "author": "Rolando MDNA",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N Panel > Bloking",
    "description": "Herramienta procedural para generar blocking anatómico de personajes y criaturas.",
    "warning": "",
    "category": "Add Mesh",
}

import bpy
from mathutils import Vector

# =========================================================================
# FUNCIONES AUXILIARES PARA GENERAR BLOQUES
# =========================================================================

def create_block(name, location, scale, subdivision_level=1):
    """
    Crea un cubo primitivo, lo nombra, escala, posiciona y 
    le añade un modificador Subdivision Surface.
    """
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    
    # Añadir modificador Subdivision Surface para suavizar el "bloque"
    mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = subdivision_level
    mod.render_levels = subdivision_level
    
    # Asegurarnos de que el origen esté en la base o extremo superior para facilitar la rotación (opcional si luego lo articulan)
    # Por ahora lo dejamos en el centro
    
    return obj

# =========================================================================
# LÓGICA DE GENERACIÓN PRINCIPAL
# =========================================================================

def generate_human_blocking(context):
    props = context.scene.bloking_props
    
    # Limpiamos bloques anteriores (Si se vuelve a generar, borrar la colección actual o agrupar)
    collection_name = "Bloking_Human"
    if collection_name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(new_collection)
    bloking_collection = bpy.data.collections[collection_name]
    
    # Activar la colección
    layer_collection = context.view_layer.layer_collection.children.get(collection_name)
    if layer_collection:
        context.view_layer.active_layer_collection = layer_collection

    # NOMBRES BASADOS EN RIGIFY (Metarig convención: spine, spine.001, head, upper_arm.L, etc. 
    # O para deformación automática: DEF-spine, DEF-upper_arm.L)
    # Usaremos una convención genérica que los auto-riggers puedan leer, o que sea clara para el artista.
    
    blocks = []
    
    # Torso Inferior (Pelvis)
    pelvis = create_block(
        name="DEF-pelvis", 
        location=(0, 0, props.height * 0.5), # Altura base del pelvis
        scale=(0.18 * props.width, 0.12 * props.width, 0.15)
    )
    blocks.append(pelvis)
    
    # Torso Superior (Pecho)
    # Lo colocamos justo encima del pelvis usando matemáticas
    chest_z = pelvis.location.z + (pelvis.scale.z / 2) + 0.15
    chest = create_block(
        name="DEF-spine.002", 
        location=(0, 0, chest_z), 
        scale=(0.22 * props.width, 0.14 * props.width, 0.20)
    )
    blocks.append(chest)
    
    # Cuello
    neck_z = chest.location.z + (chest.scale.z / 2) + 0.05
    neck = create_block(
        name="DEF-spine.004", 
        location=(0, 0, neck_z), 
        scale=(0.06, 0.06, 0.08)
    )
    blocks.append(neck)
    
    # Cabeza
    head_z = neck.location.z + (neck.scale.z / 2) + 0.12
    head = create_block(
        name="DEF-head", 
        location=(0, 0, head_z), 
        scale=(0.11 * props.head_size, 0.14 * props.head_size, 0.14 * props.head_size)
    )
    blocks.append(head)
    
    # BRAZO IZQUIERDO (L)
    # Calculamos la posición del hombro relativa al pecho
    shoulder_x = chest.scale.x / 2 + 0.08
    shoulder_z = chest.location.z + (chest.scale.z / 2) - 0.05
    
    upper_arm_L = create_block(
        name="DEF-upper_arm.L",
        location=(shoulder_x, 0, shoulder_z - (props.arm_length / 2)),
        scale=(0.06 * props.arm_width, 0.06 * props.arm_width, props.arm_length / 2)
    )
    blocks.append(upper_arm_L)
    
    forearm_L_z = upper_arm_L.location.z - (upper_arm_L.scale.z / 2) - (props.forearm_length / 2)
    forearm_L = create_block(
        name="DEF-forearm.L",
        location=(shoulder_x, 0, forearm_L_z),
        scale=(0.05 * props.arm_width, 0.05 * props.arm_width, props.forearm_length / 2)
    )
    blocks.append(forearm_L)
    
    # BRAZO DERECHO (R) - Espejo del izquierdo
    upper_arm_R = create_block(
        name="DEF-upper_arm.R",
        location=(-shoulder_x, 0, shoulder_z - (props.arm_length / 2)),
        scale=(0.06 * props.arm_width, 0.06 * props.arm_width, props.arm_length / 2)
    )
    blocks.append(upper_arm_R)
    
    forearm_R = create_block(
        name="DEF-forearm.R",
        location=(-shoulder_x, 0, forearm_L_z),
        scale=(0.05 * props.arm_width, 0.05 * props.arm_width, props.forearm_length / 2)
    )
    blocks.append(forearm_R)
    
    # MANOS
    hand_L_z = forearm_L_z - (props.forearm_length / 2) - 0.05
    hand_L = create_block(
        name="DEF-hand.L",
        location=(shoulder_x, 0, hand_L_z),
        scale=(0.04 * props.arm_width, 0.08 * props.arm_width, 0.1)
    )
    blocks.append(hand_L)
    
    hand_R = create_block(
        name="DEF-hand.R",
        location=(-shoulder_x, 0, hand_L_z),
        scale=(0.04 * props.arm_width, 0.08 * props.arm_width, 0.1)
    )
    blocks.append(hand_R)
    
    
    # PIERNA IZQUIERDA (L)
    hip_x = pelvis.scale.x / 2 - 0.05
    hip_z = pelvis.location.z - (pelvis.scale.z / 2)
    
    thigh_L = create_block(
        name="DEF-thigh.L",
        location=(hip_x, 0, hip_z - (props.thigh_length / 2)),
        scale=(0.08 * props.leg_width, 0.08 * props.leg_width, props.thigh_length / 2)
    )
    blocks.append(thigh_L)
    
    calf_L_z = thigh_L.location.z - (thigh_L.scale.z / 2) - (props.calf_length / 2)
    calf_L = create_block(
        name="DEF-shin.L",
        location=(hip_x, 0, calf_L_z),
        scale=(0.06 * props.leg_width, 0.06 * props.leg_width, props.calf_length / 2)
    )
    blocks.append(calf_L)
    
    # PIERNA DERECHA (R)
    thigh_R = create_block(
        name="DEF-thigh.R",
        location=(-hip_x, 0, hip_z - (props.thigh_length / 2)),
        scale=(0.08 * props.leg_width, 0.08 * props.leg_width, props.thigh_length / 2)
    )
    blocks.append(thigh_R)
    
    calf_R = create_block(
        name="DEF-shin.R",
        location=(-hip_x, 0, calf_L_z),
        scale=(0.06 * props.leg_width, 0.06 * props.leg_width, props.calf_length / 2)
    )
    blocks.append(calf_R)
    
    # PIES
    foot_L_z = calf_L_z - (props.calf_length / 2) - 0.05
    foot_L = create_block(
        name="DEF-foot.L",
        location=(hip_x, -0.05, foot_L_z),
        scale=(0.06 * props.leg_width, 0.15 * props.leg_width, 0.04)
    )
    blocks.append(foot_L)
    
    foot_R = create_block(
        name="DEF-foot.R",
        location=(-hip_x, -0.05, foot_L_z),
        scale=(0.06 * props.leg_width, 0.15 * props.leg_width, 0.04)
    )
    blocks.append(foot_R)
    
    # Mover todo el bloque a la colección correspondiente y deseleccionar
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


# =========================================================================
# OPERADOR
# =========================================================================

class BLOKING_OT_GenerateHuman(bpy.types.Operator):
    """Genera un humano bloqueado proceduralmente"""
    bl_idname = "object.bloking_generate_human"
    bl_label = "Generar Blocking Base"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        generate_human_blocking(context)
        return {'FINISHED'}

def update_proportions(self, context):
    """Callback llamado cada vez que se mueve un slider. Borra y recrea el modelo instantáneamente."""
    collection_name = "Bloking_Human"
    if collection_name in bpy.data.collections:
        col = bpy.data.collections[collection_name]
        for obj in col.objects:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh:
                bpy.data.meshes.remove(mesh, do_unlink=True)
                
    generate_human_blocking(context)

# =========================================================================
# PROPIEDADES / SLIDERS
# =========================================================================

class BlokingProperties(bpy.types.PropertyGroup):
    
    height: bpy.props.FloatProperty(name="Altura de Torso", default=2.0, min=0.5, max=5.0, update=update_proportions)
    width: bpy.props.FloatProperty(name="Complexión Torso", default=1.0, min=0.5, max=3.0, update=update_proportions)
    
    head_size: bpy.props.FloatProperty(name="Tamaño de Cabeza", default=1.0, min=0.3, max=3.0, update=update_proportions)
    
    arm_length: bpy.props.FloatProperty(name="Largo de Brazo", default=0.5, min=0.1, max=2.0, update=update_proportions)
    forearm_length: bpy.props.FloatProperty(name="Largo de Antebrazo", default=0.5, min=0.1, max=2.0, update=update_proportions)
    arm_width: bpy.props.FloatProperty(name="Grosor de Brazos", default=1.0, min=0.1, max=3.0, update=update_proportions)
    
    thigh_length: bpy.props.FloatProperty(name="Largo de Muslo", default=0.8, min=0.2, max=2.5, update=update_proportions)
    calf_length: bpy.props.FloatProperty(name="Largo de Pantorrilla", default=0.8, min=0.2, max=2.5, update=update_proportions)
    leg_width: bpy.props.FloatProperty(name="Grosor de Piernas", default=1.0, min=0.1, max=3.0, update=update_proportions)


# =========================================================================
# INTERFAZ (PANEL)
# =========================================================================

class VIEW3D_PT_BlokingPanel(bpy.types.Panel):
    bl_label = "Bloking (Humano)"
    bl_idname = "VIEW3D_PT_bloking_human"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI' # Esto asegura que abra en el Panel N
    bl_category = "Bloking" # Nombre de la Pestaña en el Panel N

    def draw(self, context):
        layout = self.layout
        props = context.scene.bloking_props
        
        layout.operator(BLOKING_OT_GenerateHuman.bl_idname, icon='OUTLINER_OB_ARMATURE')
        
        layout.label(text="Proporciones Generales:", icon='VIEWPORT')
        box = layout.box()
        box.prop(props, "height")
        box.prop(props, "width")
        box.prop(props, "head_size")
        
        layout.label(text="Brazos:", icon='CON_KINEMATIC')
        box = layout.box()
        box.prop(props, "arm_length")
        box.prop(props, "forearm_length")
        box.prop(props, "arm_width")
        
        layout.label(text="Piernas:", icon='CON_KINEMATIC')
        box = layout.box()
        box.prop(props, "thigh_length")
        box.prop(props, "calf_length")
        box.prop(props, "leg_width")


# =========================================================================
# REGISTRO DEL ADDON EN BLENDER
# =========================================================================

classes = (
    BlokingProperties,
    BLOKING_OT_GenerateHuman,
    VIEW3D_PT_BlokingPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bloking_props = bpy.props.PointerProperty(type=BlokingProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.bloking_props

if __name__ == "__main__":
    register()
