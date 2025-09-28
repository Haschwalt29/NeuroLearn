import React, { Suspense, useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, StatsGl, Environment, GizmoHelper, GizmoViewport } from '@react-three/drei'
import { isWebGLAvailable } from '../../utils/webgl'

// Dynamic registry for visualizations
const registry = {
  math: {
    graph: React.lazy(() => import('../math/FunctionPlot3D')),
  },
  science: {
    atom: React.lazy(() => import('../science/AtomModel')),
    pendulum: React.lazy(() => import('../science/Pendulum')),
  },
  coding: {
    linkedlist: React.lazy(() => import('../coding/LinkedList3D')),
  },
}

export default function VisualizationEngine({ type, concept, params = {}, onEvent }) {
  const webgl = isWebGLAvailable()
  const Viz = useMemo(() => {
    const group = registry[type]
    if (!group) return null
    return group[concept] || null
  }, [type, concept])

  return (
    <div className="w-full h-[520px] rounded-xl overflow-hidden border border-gray-200 bg-white">
      {!webgl && (
        <div className="w-full h-full flex items-center justify-center text-sm text-gray-600">
          WebGL is not available on this device. Showing fallback preview.
        </div>
      )}
      {webgl && (
      <Canvas camera={{ position: [4, 4, 6], fov: 50 }} dpr={[1, 2]}
        gl={{ antialias: true, powerPreference: 'high-performance' }}>
        <color attach="background" args={[0.97, 0.98, 1]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 8, 4]} intensity={1.2} />
        <Suspense fallback={null}>
          {Viz ? <Viz params={params} onEvent={onEvent} /> : null}
          <Environment preset="city" />
        </Suspense>
        <gridHelper args={[20, 20, '#e5e7eb', '#f3f4f6']} />
        <OrbitControls makeDefault enableDamping dampingFactor={0.1} />
        <GizmoHelper alignment="bottom-right" margin={[80, 80]}>
          <GizmoViewport axisColors={["#ef4444", "#10b981", "#3b82f6"]} labelColor="white" />
        </GizmoHelper>
        {/* Dev stats (toggle as needed) */}
        {/* <StatsGl showPanel={0} className="stats" /> */}
      </Canvas>
      )}
    </div>
  )
}


