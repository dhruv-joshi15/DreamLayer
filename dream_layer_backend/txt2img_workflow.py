import json
import random
import os
from dream_layer_backend_utils.workflow_loader import load_workflow
from dream_layer_backend_utils.api_key_injector import inject_api_keys_into_workflow
from dream_layer_backend_utils.update_custom_workflow import override_workflow 
from dream_layer_backend_utils.update_custom_workflow import update_custom_workflow, validate_custom_workflow
from dream_layer_backend_utils.shared_workflow_parameters import (
    inject_face_restoration_parameters,
    inject_tiling_parameters,
    inject_hires_fix_parameters,
    inject_refiner_parameters,
    inject_controlnet_parameters
)
from shared_utils import SAMPLER_NAME_MAP

def transform_to_txt2img_workflow(data):
    try:
        print("\nTransforming txt2img workflow")
        print("-" * 40)
        print(f"Data keys: {list(data.keys())}")
        
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', '')
        width = max(64, min(2048, int(data.get('width', 512))))
        height = max(64, min(2048, int(data.get('height', 512))))
        batch_size = max(1, min(8, int(data.get('batch_size', 1))))
        print(f"Batch size: {batch_size}")

        steps = max(1, min(150, int(data.get('steps', 20))))
        cfg_scale = max(1.0, min(20.0, float(data.get('cfg_scale', 7.0))))

        frontend_sampler = data.get('sampler_name', 'euler')
        sampler_name = SAMPLER_NAME_MAP.get(frontend_sampler, 'euler')
        print(f"Mapping sampler name: {frontend_sampler} -> {sampler_name}")
        scheduler = data.get('scheduler', 'normal')

        try:
            seed = int(data.get('seed', 0))
            if seed < 0:
                seed = random.randint(0, 2**32 - 1)
        except (ValueError, TypeError):
            seed = random.randint(0, 2**32 - 1)

        model_name = data.get('model', 'juggernautXL_v8Rundiffusion.safetensors')
        print(f"Using model: {model_name}")

        core_generation_settings = {
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'width': width,
            'height': height,
            'batch_size': batch_size,
            'steps': steps,
            'cfg_scale': cfg_scale,
            'sampler_name': sampler_name,
            'scheduler': scheduler,
            'seed': seed,
            'ckpt_name': model_name,
            'denoise': 1.0
        }
        print(f"Core settings: {core_generation_settings}")

        controlnet_data = data.get('controlnet', {})
        print(f"ControlNet data: {controlnet_data}")

        face_restoration_data = {
            'restore_faces': data.get('restore_faces', False),
            'face_restoration_model': data.get('face_restoration_model', 'codeformer'),
            'codeformer_weight': data.get('codeformer_weight', 0.5),
            'gfpgan_weight': data.get('gfpgan_weight', 0.5)
        }
        print(f"Face Restoration data: {face_restoration_data}")

        tiling_data = {
            'tiling': data.get('tiling', False),
            'tile_size': data.get('tile_size', 512),
            'tile_overlap': data.get('tile_overlap', 64)
        }
        print(f"Tiling data: {tiling_data}")

        hires_fix_data = {
            'hires_fix': data.get('hires_fix', False),
            'hires_fix_upscale_method': data.get('hires_fix_upscale_method', 'upscale-by'),
            'hires_fix_upscale_factor': data.get('hires_fix_upscale_factor', 2.5),
            'hires_fix_hires_steps': data.get('hires_fix_hires_steps', 1),
            'hires_fix_denoising_strength': data.get('hires_fix_denoising_strength', 0.5),
            'hires_fix_resize_width': data.get('hires_fix_resize_width', 4000),
            'hires_fix_resize_height': data.get('hires_fix_resize_height', 4000),
            'hires_fix_upscaler': data.get('hires_fix_upscaler', '4x-ultrasharp')
        }
        print(f"Hires.fix data: {hires_fix_data}")

        refiner_data = {
            'refiner_enabled': data.get('refiner_enabled', False),
            'refiner_model': data.get('refiner_model', 'none'),
            'refiner_switch_at': data.get('refiner_switch_at', 0.8)
        }
        print(f"Refiner data: {refiner_data}")

        use_controlnet = controlnet_data.get('enabled', False) and controlnet_data.get('units')
        use_lora = data.get('lora') and data.get('lora').get('enabled', False)
        use_face_restoration = face_restoration_data.get('restore_faces', False)
        use_tiling = tiling_data.get('tiling', False)

        print(f"Use ControlNet: {use_controlnet}")
        print(f"Use LoRA: {use_lora}")
        print(f"Use Face Restoration: {use_face_restoration}")
        print(f"Use Tiling: {use_tiling}")

        if model_name in ['dall-e-3', 'dall-e-2']:
            workflow_model_type = 'dalle'
        elif model_name in ['flux-pro', 'flux-dev']:
            workflow_model_type = 'bfl'
        elif 'ideogram' in model_name.lower():
            workflow_model_type = 'ideogram'
        else:
            workflow_model_type = 'local'

        workflow_request = {
            'generation_flow': 'txt2img',
            'model_name': workflow_model_type,
            'controlnet': use_controlnet,
            'lora': use_lora
        }

        print(f"Workflow request: {workflow_request}")

        workflow = load_workflow(workflow_request)
        print("Workflow loaded successfully")

        workflow = inject_api_keys_into_workflow(workflow)
        print("API keys injected")

        custom_workflow = data.get('custom_workflow')
        if custom_workflow and validate_custom_workflow(custom_workflow):
            try:
                workflow = update_custom_workflow(workflow, custom_workflow)
                print("Successfully updated custom workflow with current parameters")
            except Exception as e:
                print(f"Error updating custom workflow: {str(e)}")
                print("Falling back to default workflow override")
                workflow = override_workflow(workflow, core_generation_settings)
        else:
            workflow = override_workflow(workflow, core_generation_settings)
            print("No valid custom workflow provided, using default workflow with overrides")

        print("Core settings applied")

        if use_lora:
            from dream_layer_backend_utils.shared_workflow_parameters import inject_lora_parameters
            print("Applying LoRA parameters...")
            workflow = inject_lora_parameters(workflow, data.get('lora', {}))

        if use_controlnet:
            print("Applying ControlNet parameters...")
            workflow = inject_controlnet_parameters(workflow, controlnet_data)

        if use_face_restoration:
            print("Applying Face Restoration parameters...")
            workflow = inject_face_restoration_parameters(workflow, face_restoration_data)

        if use_tiling:
            print("Applying Tiling parameters...")
            workflow = inject_tiling_parameters(workflow, tiling_data)

        if hires_fix_data.get('hires_fix', False):
            print("Applying Hires.fix parameters...")
            workflow = inject_hires_fix_parameters(workflow, hires_fix_data)

        if refiner_data.get('refiner_enabled', False):
            print("Applying Refiner parameters...")
            workflow = inject_refiner_parameters(workflow, refiner_data)

        print("Workflow transformation complete")
        print("Generated workflow:")
        print(json.dumps(workflow, indent=2))
        return workflow

    except Exception as e:
        print(f"Error transforming workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
