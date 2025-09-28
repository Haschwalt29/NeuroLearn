import React, { useState, useMemo } from 'react'
import VisualizationEngine from '../visualizations/engine/VisualizationEngine'
import { useSocket } from '../contexts/SocketContext'

const presets = {
  math: {
    graph: {
      label: '3D Function Plotter',
      params: {
        mode: 'surface',
        expression: 'Math.sin(x) * Math.cos(z)'
      }
    }
  },
  science: {
    atom: {
      label: 'Atom with Electrons',
      params: { electrons: 4 }
    },
    pendulum: {
      label: 'Pendulum (physics)',
      params: { length: 2, gravity: 9.81, damping: 0.01 }
    }
  },
  coding: {
    linkedlist: {
      label: 'Linked List (insert/delete)',
      params: { values: [1, 4, 2, 8, 5], activeIndex: 2 }
    }
  }
}

export default function VisualizationLab() {
  const [type, setType] = useState('math')
  const [concept, setConcept] = useState('graph')
  const config = useMemo(() => presets[type][concept], [type, concept])
  const { emit } = useSocket()
  const [expression, setExpression] = useState('Math.sin(x) * Math.cos(z)')
  const [electrons, setElectrons] = useState(4)
  const [length, setLength] = useState(2)
  const [gravity, setGravity] = useState(9.81)
  const [damping, setDamping] = useState(0.01)

  const onEvent = (evt) => {
    emit('viz_event', { ...evt, type, concept, ts: Date.now() })
    if (evt.type === 'linkedlist_insert' || evt.type === 'linkedlist_remove') {
      emit('quest_progress', { action: 'viz_interaction', meta: evt })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <select value={type} onChange={(e) => { setType(e.target.value); setConcept(Object.keys(presets[e.target.value])[0]) }} className="border rounded-md px-3 py-2">
          <option value="math">Math</option>
          <option value="science">Science</option>
          <option value="coding">Coding</option>
        </select>
        <select value={concept} onChange={(e) => setConcept(e.target.value)} className="border rounded-md px-3 py-2">
          {Object.keys(presets[type]).map((k) => (
            <option key={k} value={k}>{presets[type][k].label}</option>
          ))}
        </select>
      </div>

      {/* Controls */}
      <div className="bg-white border rounded-lg p-3 flex flex-wrap items-center gap-3">
        {type === 'math' && concept === 'graph' && (
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">f(x,z)=</label>
            <input value={expression} onChange={(e) => setExpression(e.target.value)} className="border px-2 py-1 rounded text-sm w-[280px]" />
          </div>
        )}
        {type === 'science' && concept === 'atom' && (
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">electrons</label>
            <input type="range" min={1} max={8} value={electrons} onChange={(e) => setElectrons(Number(e.target.value))} />
            <span className="text-sm">{electrons}</span>
          </div>
        )}
        {type === 'science' && concept === 'pendulum' && (
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">length</label>
              <input type="range" min={1} max={4} step={0.1} value={length} onChange={(e) => setLength(Number(e.target.value))} />
              <span className="text-sm">{length.toFixed(1)}</span>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">gravity</label>
              <input type="range" min={1} max={20} step={0.1} value={gravity} onChange={(e) => setGravity(Number(e.target.value))} />
              <span className="text-sm">{gravity.toFixed(1)}</span>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">damping</label>
              <input type="range" min={0} max={0.05} step={0.005} value={damping} onChange={(e) => setDamping(Number(e.target.value))} />
              <span className="text-sm">{damping.toFixed(3)}</span>
            </div>
          </div>
        )}
      </div>

      <VisualizationEngine
        type={type}
        concept={concept}
        params={{
          ...(config.params || {}),
          ...(type === 'math' && concept === 'graph' ? { expression } : {}),
          ...(type === 'science' && concept === 'atom' ? { electrons } : {}),
          ...(type === 'science' && concept === 'pendulum' ? { length, gravity, damping } : {}),
        }}
        onEvent={onEvent}
      />
    </div>
  )
}


