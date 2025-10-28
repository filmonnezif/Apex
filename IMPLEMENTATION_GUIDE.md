# Implementation Guide - 3D Product Viewer & Optimization Page

This guide explains the three major updates implemented in the Apex AI Dynamic Price Optimization platform.

## ✅ Changes Implemented

### 1. Added Sixth Product
**File:** `/backend/routes/price_routes.py`

Added a new product to the mock database:
```python
{
    "id": "NES006",
    "name": "Milo Energy Drink 400g",
    "category": "standard",
    "current_price": 18.50,
    "cost": 7.50,
    "unit": "tin"
}
```

### 2. 3D Product Visualization with Three.js
**Files Created:**
- `/frontend/components/ProductViewer3D.vue` - 3D product viewer component

**Dependencies Added:**
- `three@^0.159.0` - Three.js library for 3D rendering

**Features:**
- Interactive 3D product models that rotate automatically
- Orbit controls (drag to rotate, scroll to zoom)
- Different shapes for different products:
  - **Cylinder:** Coffee, Milk Powder, Milo
  - **Box:** Chocolate, Noodles
  - **Bottle:** Water (multi-part 3D model)
- Realistic lighting and materials
- Responsive to container size

**Product Configurations:**
```javascript
const productConfigs = {
  'NES001': { color: 0x8B4513, shape: 'cylinder', label: 'Coffee' },
  'NES002': { color: 0xD2691E, shape: 'box', label: 'Chocolate' },
  'NES003': { color: 0x87CEEB, shape: 'bottle', label: 'Water' },
  'NES004': { color: 0xFF6347, shape: 'box', label: 'Noodles' },
  'NES005': { color: 0xFFFFE0, shape: 'cylinder', label: 'Milk Powder' },
  'NES006': { color: 0x228B22, shape: 'cylinder', label: 'Milo' }
}
```

### 3. Dedicated Optimization Page
**Files Created:**
- `/frontend/pages/optimize/[id].vue` - Dynamic route for product optimization

**Changes to Existing Files:**
- `/frontend/pages/index.vue` - Removed modal, added navigation to optimization page
- `/frontend/pages/products.vue` - Updated to navigate to optimization page

**Features:**
- Clean, dedicated page for each product optimization
- Back button to return to dashboard
- 3D product viewer integrated in header
- All optimization data displayed on single page
- URL structure: `/optimize/NES001`, `/optimize/NES002`, etc.

## 📚 How to Use Three.js in This Project

### Basic Structure
```vue
<template>
  <div ref="containerRef"></div>
</template>

<script setup>
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

const containerRef = ref(null)

const initThreeJS = () => {
  // 1. Create scene
  const scene = new THREE.Scene()
  
  // 2. Create camera
  const camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000)
  
  // 3. Create renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true })
  
  // 4. Add objects to scene
  const geometry = new THREE.BoxGeometry(1, 1, 1)
  const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 })
  const cube = new THREE.Mesh(geometry, material)
  scene.add(cube)
  
  // 5. Add lighting
  const light = new THREE.DirectionalLight(0xffffff, 1)
  scene.add(light)
  
  // 6. Animation loop
  const animate = () => {
    requestAnimationFrame(animate)
    renderer.render(scene, camera)
  }
  animate()
}

onMounted(() => {
  initThreeJS()
})
</script>
```

### Available Geometries in Three.js
- **BoxGeometry** - Rectangular boxes
- **SphereGeometry** - Spheres
- **CylinderGeometry** - Cylinders (cans, jars)
- **ConeGeometry** - Cones
- **TorusGeometry** - Donuts
- **PlaneGeometry** - Flat planes
- **Custom Shapes** - Using BufferGeometry

### Material Types
- **MeshBasicMaterial** - No lighting
- **MeshStandardMaterial** - Realistic, responds to lights
- **MeshPhongMaterial** - Shiny surfaces
- **MeshLambertMaterial** - Matte surfaces
- **MeshPhysicalMaterial** - Most realistic

### Lighting Options
- **AmbientLight** - Global illumination
- **DirectionalLight** - Sun-like light
- **PointLight** - Light bulb effect
- **SpotLight** - Flashlight effect

## 🚀 Testing the Implementation

### 1. Start the Backend
```bash
cd /workspaces/docker-in-docker-2/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend
```bash
cd /workspaces/docker-in-docker-2/frontend
npm run dev
```

### 3. Test the Features
1. **View 6 Products** - Dashboard should show all 6 products including "Milo Energy Drink"
2. **3D Viewer** - Click any product to see the 3D model on optimization page
3. **Optimization** - Click "Run Price Optimization" to see AI recommendations
4. **Navigation** - Use back button to return to dashboard

## 🎨 Customizing 3D Models

### Change Product Color
```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0xFF5733,  // Hex color
  roughness: 0.4,   // 0 = shiny, 1 = rough
  metalness: 0.3    // 0 = non-metallic, 1 = metallic
})
```

### Change Product Shape
```javascript
// Box
const geometry = new THREE.BoxGeometry(width, height, depth)

// Cylinder
const geometry = new THREE.CylinderGeometry(radiusTop, radiusBottom, height, segments)

// Sphere
const geometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments)
```

### Add Textures
```javascript
const textureLoader = new THREE.TextureLoader()
const texture = textureLoader.load('/path/to/texture.jpg')
const material = new THREE.MeshStandardMaterial({ map: texture })
```

## 📁 File Structure
```
frontend/
├── components/
│   ├── DemandChart.vue
│   ├── ProfitChart.vue
│   └── ProductViewer3D.vue    ← NEW: 3D viewer component
├── pages/
│   ├── index.vue                ← UPDATED: Removed modal
│   ├── products.vue             ← UPDATED: Navigation
│   └── optimize/
│       └── [id].vue             ← NEW: Optimization page
└── package.json                 ← UPDATED: Added Three.js

backend/
└── routes/
    └── price_routes.py          ← UPDATED: Added 6th product
```

## 🔧 Advanced Three.js Features

### Loading 3D Models (GLTF/GLB)
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'

const loader = new GLTFLoader()
loader.load('/models/product.glb', (gltf) => {
  scene.add(gltf.scene)
})
```

### Adding Shadows
```javascript
renderer.shadowMap.enabled = true
light.castShadow = true
mesh.castShadow = true
mesh.receiveShadow = true
```

### Post-Processing Effects
```javascript
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass'
import { BloomPass } from 'three/examples/jsm/postprocessing/BloomPass'

const composer = new EffectComposer(renderer)
composer.addPass(new RenderPass(scene, camera))
composer.addPass(new BloomPass(1.5))
```

## 🐛 Common Issues & Solutions

### Issue: Three.js not rendering
**Solution:** Check that container has dimensions:
```css
.container {
  width: 100%;
  height: 400px; /* Must have explicit height */
}
```

### Issue: Black screen
**Solution:** Add lighting:
```javascript
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
scene.add(ambientLight)
```

### Issue: Memory leaks
**Solution:** Cleanup in onUnmounted:
```javascript
onUnmounted(() => {
  renderer.dispose()
  geometry.dispose()
  material.dispose()
})
```

## 📖 Additional Resources

- **Three.js Documentation:** https://threejs.org/docs/
- **Three.js Examples:** https://threejs.org/examples/
- **Three.js Journey Course:** https://threejs-journey.com/
- **WebGL Fundamentals:** https://webglfundamentals.org/

## 🎯 Next Steps

### Potential Enhancements:
1. **Load Real 3D Models** - Use GLB/GLTF files for actual product models
2. **Product Labels** - Add text overlays to 3D models
3. **Multiple Views** - Front, side, top views
4. **AR Support** - WebXR for augmented reality preview
5. **Animation** - Product opening/closing animations
6. **Comparison View** - Side-by-side 3D product comparisons

### Performance Optimization:
1. **LOD (Level of Detail)** - Simpler models when far away
2. **Instancing** - Reuse geometry for multiple objects
3. **Texture Compression** - Use compressed texture formats
4. **Lazy Loading** - Load 3D models only when needed
