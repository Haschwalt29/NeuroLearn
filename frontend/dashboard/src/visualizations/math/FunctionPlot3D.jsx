import React, { useMemo } from 'react'
import * as THREE from 'three'
import { Line, Html } from '@react-three/drei'

function generateSurface(fn, xRange, zRange, step) {
  const geometry = new THREE.BufferGeometry()
  const vertices = []
  for (let x = xRange[0]; x <= xRange[1]; x += step) {
    for (let z = zRange[0]; z <= zRange[1]; z += step) {
      let y = fn(x, z)
      if (!Number.isFinite(y)) y = 0
      vertices.push(x, y, z)
    }
  }
  const position = new Float32Array(vertices)
  geometry.setAttribute('position', new THREE.BufferAttribute(position, 3))
  return geometry
}

export default function FunctionPlot3D({ params = {}, onEvent }) {
  const {
    mode = 'surface',
    // y = f(x) when singleVar, otherwise y = f(x,z)
    expression = 'Math.sin(x) * Math.cos(z)',
    xRange = [-3, 3],
    zRange = [-3, 3],
    step = 0.15,
    color = '#2563eb',
  } = params

  const { fn, error } = useMemo(() => {
    try {
      const cleaned = String(expression)
        .replace(/\^/g, '**')
        .replace(/[^0-9+\-*/()xz., a-zA-Z_*^]|\s{2,}/g, (m) => m.trim())
      // Allow bare Math functions by using a Math sandbox
      // Users can type: sin(x) * cos(z), exp(x), sqrt(x*x+z*z), etc.
      // eslint-disable-next-line no-new-func
      const f = new Function('x', 'z', `with (Math) { return ${cleaned}; }`)
      // Probe once to ensure it runs
      void f(0, 0)
      return { fn: f, error: null }
    } catch (e) {
      console.error(e)
      return { fn: () => 0, error: e?.message || 'Invalid expression' }
    }
  }, [expression])

  const surface = useMemo(() => {
    if (mode !== 'surface') return null
    return generateSurface(fn, xRange, zRange, step)
  }, [fn, xRange, zRange, step, mode])

  const axes = useMemo(() => {
    const lines = []
    const axisLen = 4.5
    lines.push({ start: [0, 0, 0], end: [axisLen, 0, 0], color: '#ef4444' }) // X
    lines.push({ start: [0, 0, 0], end: [0, axisLen, 0], color: '#10b981' }) // Y
    lines.push({ start: [0, 0, 0], end: [0, 0, axisLen], color: '#3b82f6' }) // Z
    return lines
  }, [])

  return (
    <group>
      {/* Axes */}
      {axes.map((l, i) => (
        <Line key={i} points={[l.start, l.end]} color={l.color} lineWidth={2} />
      ))}

      {/* Labels */}
      <Html position={[4.7, 0, 0]} center style={{ pointerEvents: 'none' }}>x</Html>
      <Html position={[0, 4.7, 0]} center style={{ pointerEvents: 'none' }}>y</Html>
      <Html position={[0, 0, 4.7]} center style={{ pointerEvents: 'none' }}>z</Html>

      {/* Surface or curve */}
      {mode === 'surface' && surface && (
        <mesh>
          <bufferGeometry attach="geometry" {...surface} />
          <meshStandardMaterial color={color} wireframe opacity={0.9} transparent />
        </mesh>
      )}

      {/* Simple hotspot tooltip */}
      {(() => {
        let y0 = 0
        try {
          const val = fn ? fn(0, 0) : 0
          y0 = Number.isFinite(val) ? val : 0
        } catch (_) {
          y0 = 0
        }
        const label = Number.isFinite(y0) ? y0.toFixed(2) : '—'
        return (
          <group position={[0, y0, 0]}>
            <mesh onPointerOver={() => onEvent && onEvent({ type: 'tooltip', label: 'f(0,0)', value: y0 })}>
              <sphereGeometry args={[0.05, 8, 8]} />
              <meshStandardMaterial color="#f43f5e" />
            </mesh>
            <Html distanceFactor={10} style={{ background: 'rgba(255,255,255,0.9)', padding: 4, borderRadius: 4, fontSize: 12 }}>
              f(0,0) = {label}
            </Html>
          </group>
        )
      })()}

      {error && (
        <Html position={[0, 4.2, 0]} center>
          <div className="text-xs px-2 py-1 rounded bg-red-100 text-red-700 border border-red-300 shadow-sm">
            Invalid expression: {error}
          </div>
        </Html>
      )}
    </group>
  )
}


