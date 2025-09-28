import React, { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

export default function Pendulum({ params = {}, onEvent }) {
  const { length = 2, gravity = 9.81, damping = 0.01, theta0 = 0.6 } = params
  const rod = useRef()
  const bob = useRef()
  // Simple integrator
  const state = useRef({ theta: theta0, omega: 0 })

  useFrame((_, dt) => {
    const { theta, omega } = state.current
    const alpha = -(gravity / length) * Math.sin(theta) - damping * omega
    const newOmega = omega + alpha * dt
    const newTheta = theta + newOmega * dt
    state.current.theta = newTheta
    state.current.omega = newOmega

    const x = length * Math.sin(newTheta)
    const y = -length * Math.cos(newTheta)
    if (rod.current) rod.current.rotation.z = newTheta
    if (bob.current) bob.current.position.set(x, y, 0)
  })

  return (
    <group position={[0, 1.5, 0]}>
      {/* Pivot */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshStandardMaterial color="#111827" />
      </mesh>
      {/* Rod */}
      <mesh ref={rod} position={[0, -length / 2, 0]}>
        <boxGeometry args={[0.02, length, 0.02]} />
        <meshStandardMaterial color="#6b7280" />
      </mesh>
      {/* Bob */}
      <mesh ref={bob}>
        <sphereGeometry args={[0.12, 18, 18]} />
        <meshStandardMaterial color="#2563eb" />
      </mesh>
    </group>
  )
}


