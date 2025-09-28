import React, { useMemo, useRef, useState, useCallback } from 'react'
import { Line, Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

function NodeBox({ position, value, highlight }) {
  return (
    <group position={position}>
      <mesh>
        <boxGeometry args={[0.8, 0.4, 0.4]} />
        <meshStandardMaterial color={highlight ? '#10b981' : '#64748b'} />
      </mesh>
      <Html center position={[0, 0, 0.26]} style={{ pointerEvents: 'none' }}>
        <div style={{ fontSize: 12, color: '#111827' }}>{value}</div>
      </Html>
    </group>
  )
}

export default function LinkedList3D({ params = {}, onEvent }) {
  const { values = [3, 7, 2, 9], activeIndex = 1 } = params
  const [list, setList] = useState(values)
  const nodes = useMemo(() => list.map((v, i) => ({ value: v, x: i * 1.2 })), [list])
  const pulse = useRef(0)
  useFrame((state) => {
    pulse.current = (Math.sin(state.clock.getElapsedTime() * 3) + 1) / 2
  })
  const insert = useCallback((index, value) => {
    setList((prev) => {
      const next = [...prev]
      next.splice(index, 0, value)
      onEvent && onEvent({ type: 'linkedlist_insert', index, value })
      return next
    })
  }, [onEvent])
  const remove = useCallback((index) => {
    setList((prev) => {
      const next = [...prev]
      const [value] = next.splice(index, 1)
      onEvent && onEvent({ type: 'linkedlist_remove', index, value })
      return next
    })
  }, [onEvent])
  return (
    <group>
      {nodes.map((n, i) => (
        <NodeBox key={i} position={[n.x, 0, 0]} value={n.value} highlight={i === activeIndex && pulse.current > 0.5} />
      ))}
      {nodes.slice(0, -1).map((n, i) => (
        <Line key={`arrow-${i}`} points={[[n.x + 0.5, 0, 0], [n.x + 0.9, 0, 0]]} color="#111827" lineWidth={2} />
      ))}
      {/* Simple controls overlay for demo */}
      <Html position={[0, 1.1, 0]} center>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => insert(nodes.length, Math.floor(Math.random() * 10))} className="px-2 py-1 text-xs bg-blue-600 text-white rounded">Insert</button>
          {nodes.length > 0 && (
            <button onClick={() => remove(nodes.length - 1)} className="px-2 py-1 text-xs bg-red-600 text-white rounded">Delete</button>
          )}
        </div>
      </Html>
    </group>
  )
}


