import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function Electron({ radius = 1.5, speed = 1, tilt = 0.5 }) {
  const group = useRef()
  const sphere = useRef()
  useFrame((state) => {
    const t = state.clock.getElapsedTime() * speed
    const x = Math.cos(t) * radius
    const z = Math.sin(t) * radius * Math.cos(tilt)
    const y = Math.sin(t) * radius * Math.sin(tilt)
    if (group.current) group.current.position.set(x, y, z)
    if (sphere.current) sphere.current.rotation.y = t
  })
  return (
    <group ref={group}>
      <mesh ref={sphere}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={0.6} />
      </mesh>
    </group>
  )
}

export default function AtomModel({ params = {} }) {
  const { electrons = 3, nucleusColor = '#ef4444' } = params
  const electronConfigs = Array.from({ length: electrons }).map((_, i) => ({
    radius: 1.2 + (i * 0.4),
    speed: 0.8 + i * 0.3,
    tilt: 0.3 + i * 0.2,
  }))

  return (
    <group>
      {/* Nucleus */}
      <mesh>
        <sphereGeometry args={[0.35, 24, 24]} />
        <meshStandardMaterial color={nucleusColor} roughness={0.4} metalness={0.1} />
      </mesh>
      {/* Electron orbits */}
      {electronConfigs.map((cfg, idx) => (
        <Electron key={idx} radius={cfg.radius} speed={cfg.speed} tilt={cfg.tilt} />
      ))}
    </group>
  )
}


