#Author: NSA Cloud
bl_info = {
    "name": "SF6 Modding Tools",
    "author": "Dashgua",
    "version": (0, 1),
    "blender": (4, 2, 0),
    "description": "Toolbox to assist creating mods for street fighter 6",
    "warning": ""
	}

import bpy
import os
import sys

from bpy.types import AddonPreferences, Operator, Panel
from bpy.props import BoolProperty

specials = {
    "Bip001-Pelvis": "Bip001-Spine",
    "Bone_Forearm_L_01": "Bip001-L-UpperArm",
    "Bone_Forearm_R_01": "Bip001-R-UpperArm",
    "Bip001-L-Calf" : "Bone_knee_root_L",
    "Bip001-R-Calf" : "Bone_knee_root_R"
}

def get_prefs():
    return bpy.context.preferences.addons[__name__].preferences

class ToolPreferences(AddonPreferences):
    bl_idname = __name__

    use_face_conv : BoolProperty(name="Face converison", description="use conversion mapping for face model", default=False)
    
class ToolboxPanel(Panel):
    bl_label = "SF6 Toolbox: Modding Tools"
    bl_idname = "sf6_toolbox_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "SF6 Toolbox"

    @classmethod
    def poll(self,context):
        return context is not None

    def draw(self, context):
        prefs = get_prefs()
        layout = self.layout
        layout.prop(prefs, "use_face_conv")
        layout.operator("sf6_toolbox.prune_armature")
        layout.operator("sf6_toolbox.snap_armature")
        layout.operator("sf6_toolbox.rename_vgs")
        layout.operator("sf6_toolbox.rename_meshes")

def get_face_root():
    root = None
    for obj in bpy.context.selected_objects:
        if obj.type != 'ARMATURE':
            continue        
        for bone in obj.data.bones:
            if bone.name.startswith("Bone_face"):
                root = bone.name
            
    assert(root is not None)
    return root

class Converter():
    def snowbreak_to_sf6_face():
        face_conv = {
#            "Bone_face008" : "C_FaceRoot",
            "upperLidMain1_L" : "L_eye_Top",
            "upperLidMain4_L" : "L_eye_lid_up_00",
#            "upperLidMain6_L" : "",
            "upperLidMain8_L" : "L_eye_lid_up_01",
            "upperLidMain11_L" : "L_eye_End",
            "lowerLidMain3_L" : "L_eye_lid_bottom_00",
#            "lowerLidMain5_L" : "",
            "lowerLidMain8_L" : "L_eye_lid_bottom_01",
            "EyeBrowInnerJoint_L" : "L_eyebrow_Up_00",
#            "EyeBrowMid1Joint_L" : "",
            "EyeBrowMid2Joint_L" : "L_eyebrow_Up_01",
#            "EyeBrowMid3Joint_L" : "",
            "EyeBrowOuterJoint_L" : "L_eyebrow_Up_02",
            "LipJoint_L" : "L_out_lip_corner",
            "upperLipJoint3_L" : "L_out_lip_up_01",
            "lowerLipJoint3_L" : "L_out_lip_bottom_02",
            "upperTeethJoint_M" : "C_UpJaw",
            "lowerTeethJoint_M" : "C_UnderJaw",
            "JawJoint_M" : "C_jaw_Grp",
            "Tongue0Joint_M" : "C_tongue_00",
            "Tongue1Joint_M" : "C_tongue_01",
            "EyeJoint_L" : "L_eye",
            "IrisJoint_L" : "L_iris"
        }
        
        
        mirror = {}
        for k, v in face_conv.items():
            mirror[k.replace("_L", "_R")] = v.replace("L_", "R_")
        face_conv.update(mirror)

        return face_conv
        
    def snowbreak_to_sf6():
        conv = {
            "root_01" : "Root",
            "Bip001-Head" : "C_Head",
            "Bip001-L-Thigh" : "L_Thigh",
            "Bip001-L-Calf" : "L_Calf_HJ_01",
            "Bip001-L-Foot" : "L_Foot",
            "Bip001-L-Toe0" : "L_Metatarsal",
            "Bip001-L-Clavicle" : "L_Trapezius_HJ_02",
            "Bip001-L-UpperArm" : "L_UpperArm",
            "Bip001-L-Forearm" : "L_ForeArm",
            "Bip001-L-Hand" : "L_Hand",
            "Bip001-L-Finger0" : "L_Thumb1",
            "Bip001-L-Finger01" : "L_Thumb2",
            "Bip001-L-Finger02" : "L_Thumb3",
            "Bip001-L-Finger1" : "L_Index1",
            "Bip001-L-Finger11" : "L_Index2",
            "Bip001-L-Finger12" : "L_Index3",
            "Bip001-L-Finger2" : "L_Middle1",
            "Bip001-L-Finger21" : "L_Middle2",
            "Bip001-L-Finger22" : "L_Middle3",
            "Bip001-L-Finger3" : "L_Ring2",
            "Bip001-L-Finger31" : "L_Ring3",
            "Bip001-L-Finger32" : "L_Ring4",
            "Bip001-L-Finger4" : "L_Pinky2",
            "Bip001-L-Finger41" : "L_Pinky3",
            "Bip001-L-Finger42" : "L_Pinky4",
#            "Bip001-Pelvis" : "C_Hip",
            "Bip001-Neck" : "C_Neck",
            "Bip001-Neck2" : "C_Neck1",
            "Bip001-Spine" : "C_Spine1",
            "Bip001-Spine2" : "C_Spine2",
            "Bip001-Spine3" : "C_Chest",
            "Bone_knee_root_L" : "L_Knee",
            "Bone_knee_L_03" : "L_Hamstring_HJ_01",
            "Bone_knee_L_04" : "L_CalfJiggle_HJ_01"
        }
        
        mirror_rules = [("-L-", "-R-"), ("_L", "_R"), ("_l", "_r")]
        mirror = {}
        for k, v in conv.items():
            for rule in mirror_rules:
                if rule[0] in k:
                    mirror[k.replace(rule[0], rule[1])] = v.replace("L_", "R_")
        conv.update(mirror)

        return conv

    def sf6_to_snowbreak():
        conv = Converter.snowbreak_to_sf6()
        rconv = {}
        for k, v in conv.items():
            rconv[v] = k
        print(conv)
        return rconv

    def sf6_to_snowbreak_face():
        conv = Converter.snowbreak_to_sf6_face()
        rconv = {}
        for k, v in conv.items():
            rconv[v] = k
        return rconv
    
def get_objects():
    return bpy.context.view_layer.objects

def get_meshes_objects(armature_name):
    meshes = []
    for ob in get_objects():
        if ob.type == 'MESH':
            if ob.parent:
                if ob.parent.type == 'ARMATURE' and ob.parent.name == armature_name:
                    meshes.append(ob)
                elif ob.parent.parent and ob.parent.parent.type == 'ARMATURE' and ob.parent.parent.name == armature_name:
                    meshes.append(ob)
    return meshes

def mix_weights(mesh, vg_from, vg_to, mix_strength=1.0, mix_mode='ADD', delete_old_vg=True):
    mesh.active_shape_key_index = 0
    mod = mesh.modifiers.new("VertexWeightMix", 'VERTEX_WEIGHT_MIX')
    mod.vertex_group_a = vg_to
    mod.vertex_group_b = vg_from
    mod.mix_mode = mix_mode
    mod.mix_set = 'B'
    mod.mask_constant = mix_strength

    bpy.ops.object.modifier_apply(modifier=mod.name)

    if delete_old_vg:
        mesh.vertex_groups.remove(mesh.vertex_groups.get(vg_from))
    mesh.active_shape_key_index = 0

def remove_weights(mesh, vg):
    mesh.vertex_groups.remove(mesh.vertex_groups.get(vg))


def unselect_all():
    for obj in get_objects():
        select(obj, False)


def set_active(obj, skip_sel=False):
    if not skip_sel:
        select(obj)
    bpy.context.view_layer.objects.active = obj


def select(obj, sel=True):
    obj.select_set(sel)

def check_bone_exists(armature, target_bone):
    for bone in armature.bones:
        if bone.name == target_bone:
            return True
    return False

class PruneArmature(Operator):
    bl_label = "Prune armature"
    bl_idname = "sf6_toolbox.prune_armature"
    bl_options = {'REGISTER', 'UNDO'}
  
    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        return obj is not None and bool( obj.type == "ARMATURE" ) and bool(bpy.context.object.mode == "OBJECT")

    def is_body_bone(self, bone):
        body_keywords = ["Bip001", "LOD", "lod", "hair_bone", "Bone"]
        for keyword in body_keywords:
            if keyword in bone:
                return True
        return False
     
    def merge_weights(self, armature_obj, target_parent, use_face_conv):
        num_merged_bone = 0
        for mesh in get_meshes_objects(armature_obj.name):
            set_active(mesh)
            
            for bone, parent in target_parent.items():
                if bone == parent:
                    continue
                
                if not mesh.vertex_groups.get(bone):
                    continue
                
                if not use_face_conv and not self.is_body_bone(bone):
                    remove_weights(mesh, bone)
                    continue
                
                if not mesh.vertex_groups.get(parent):
                    mesh.vertex_groups.new(name=parent)
                mix_weights(mesh, bone, parent)

        unselect_all()
        set_active(armature_obj)
        bpy.ops.object.mode_set(mode='EDIT')
        for bone, parent in target_parent.items():
            if bone != parent:
                armature_obj.data.edit_bones.remove(armature_obj.data.edit_bones.get(bone))
                num_merged_bone += 1
        bpy.ops.object.mode_set(mode='OBJECT')

        return num_merged_bone

    def get_parenting(self, armature, cur_bone, conv, target):
        if cur_bone in specials and check_bone_exists(armature, specials[cur_bone]):
            target[cur_bone] = specials[cur_bone]
        elif cur_bone in conv:
            target[cur_bone] = cur_bone
        else:
            par = armature.bones[cur_bone].parent
            target[cur_bone] = target[par.name]

        for child in armature.bones[cur_bone].children:
            self.get_parenting(armature, child.name, conv, target)

    def execute(self, context):
        prefs = get_prefs()
   
        if prefs.use_face_conv:
            conv = Converter.snowbreak_to_sf6_face()
            root = get_face_root()
            conv[root] = "C_FaceRoot"
        else:
            conv = Converter.snowbreak_to_sf6()
            root = 'root_01'
            
        armature_obj = bpy.context.active_object
        armature = armature_obj.data
        
        target_parent = {}
        self.get_parenting(armature, root, conv, target_parent)
        
        self.merge_weights(armature_obj, target_parent, prefs.use_face_conv)
        
        self.report({'INFO'}, 'Completed')
        return {'FINISHED'}
    
class SnapArmature(Operator):
    bl_label = "Snap armature"
    bl_idname = "sf6_toolbox.snap_armature"
    bl_options = {'REGISTER', 'UNDO'}
  
    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects) != 2:
            return False
        for obj in bpy.context.selected_objects:
            if obj.type != "ARMATURE":
                return False
        if bpy.context.object.mode != "OBJECT":
            return False
        return True
    
    def execute(self, context):
        prefs = get_prefs()
        if prefs.use_face_conv:
            conv = Converter.sf6_to_snowbreak_face()        
            conv["C_FaceRoot"] = get_face_root()
        else:
            conv = Converter.sf6_to_snowbreak()
        
        armature = bpy.context.active_object.data
        armature.use_mirror_x = False

        origial_bones = [bone.name for bone in armature.bones]
        bpy.ops.object.join()
        extra_bones = []
        for bone in armature.bones:
            if bone.name not in origial_bones:
                extra_bones.append(bone.name)
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.area.type = 'VIEW_3D'
        for k, v in conv.items():
            if k == "Root" or v not in armature.edit_bones or k not in armature.edit_bones:
                continue
            
            armature.edit_bones.active = armature.edit_bones[v]
            bpy.ops.armature.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=k, case_sensitive=False, extend=True)
            bpy.ops.object.select_pattern(pattern=v, case_sensitive=False, extend=True)
            bpy.ops.view3d.snap_selected_to_active()
            bpy.ops.armature.select_all(action='DESELECT')
        
        for bone in extra_bones:
            armature.edit_bones.active = armature.edit_bones[bone]
            bpy.ops.armature.delete()

            
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, 'Completed')
        return {'FINISHED'}

    
class RenameVertexGroups(Operator):
    bl_label = "Rename vertex groups"
    bl_idname = "sf6_toolbox.rename_vgs"
    bl_options = {'REGISTER', 'UNDO'}
  
    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        return obj is not None and bool( obj.type == "ARMATURE" ) and bool(bpy.context.object.mode == "OBJECT")

    def execute(self, context):
        prefs = get_prefs()
        if prefs.use_face_conv:
            conv = Converter.snowbreak_to_sf6_face()
        else:
            conv = Converter.snowbreak_to_sf6()
        
        armature_obj = bpy.context.active_object
        
        num_vgs = 0
        for mesh in get_meshes_objects(armature_obj.name):
            vgs = mesh.vertex_groups
            num_vgs += len(vgs)
            for key, vg in vgs.items():
                if key in conv.values():
                    continue
                if prefs.use_face_conv and key.startswith("Bone_face"):
                    vg.name = "C_FaceRoot"
                elif key in conv:
                    vg.name = conv[key]
                else:
                    vgs.remove(vg)
                    
            
        self.report({'INFO'}, 'Completed {}'.format(num_vgs))
        return {'FINISHED'}


class RenameMeshToREFormat(Operator):
    bl_label = "Rename meshes"
    bl_idname = "sf6_toolbox.rename_meshes"
    bl_description = "Renames selected meshes to RE mesh naming scheme (Example: Group_0_Sub_0__Shirts_Mat)"
    bl_options = {'REGISTER', 'UNDO'}
 
    @classmethod
    def poll(cls, context):
        if context.selected_objects == []:
            return False
        for obj in context.selected_objects:
            if not (bool( obj.type == "MESH" )):
                return False
        return True    
    
    def execute(self, context):
        objWithMatNameList = []
        for selectedObj in context.selected_objects:
            if selectedObj.type == "MESH":
                if len(selectedObj.data.materials) > 0:
                    materialName = selectedObj.data.materials[0].name.split(".",1)[0].strip()
                else:
                    continue
                
                if not materialName.startswith("girl") or ("eye" in materialName and "shadow" in materialName):
                    continue
                
                objWithMatNameList.append((selectedObj, materialName))
        
        groupID = 0
        groupIndex = 0

        for obj, materialName in objWithMatNameList:
            newMaterialName = ""
            for s in materialName.split('_'):
                if s == "" or s.startswith("girl") or s == "inst":
                    continue
                
                if newMaterialName == "":
                    if s[0].isalpha():
                        newMaterialName = s
                else:
                    if s[0].isalpha():
                        newMaterialName += s[0]
                    else:
                        newMaterialName += s
            
            newMaterialName = "esf_" + newMaterialName
            obj.data.materials[0].name = newMaterialName
            obj.name = f"Group_{str(groupID)}_Sub_{str(groupIndex)}__{newMaterialName}"
            groupIndex += 1
        
        self.report({"INFO"},"Renamed selected objects to RE Mesh format")
        return {'FINISHED'}

# Registration
classes = [
    ToolPreferences,
    ToolboxPanel,
    PruneArmature,
    SnapArmature,
    RenameVertexGroups,
    RenameMeshToREFormat
]


def register():
	for classEntry in classes:
		bpy.utils.register_class(classEntry)

def unregister():
	for classEntry in classes:
		bpy.utils.unregister_class(classEntry)
        
if __name__ == '__main__':
    register()