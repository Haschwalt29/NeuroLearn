import React, { useEffect, useMemo, useRef } from 'react'
import * as d3 from 'd3'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'

export default function KnowledgeGraph({ userId }) {
  const svgRef = useRef(null)
  const { token } = useAuth()

  useEffect(() => {
    let isMounted = true
    let cleanup = () => {}
    async function load() {
      const res = await axios.get(`/api/knowledge-graph/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!isMounted) return
      const { nodes, edges } = res.data

      const width = 720
      const height = 420
      const svg = d3.select(svgRef.current)
      svg.selectAll('*').remove()
      svg.attr('viewBox', [0, 0, width, height])

      const color = d3.scaleSequential(d3.interpolateBlues).domain([0, 1])

      const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(edges).id(d => d.id).distance(80))
        .force('charge', d3.forceManyBody().strength(-160))
        .force('center', d3.forceCenter(width / 2, height / 2))

      const link = svg.append('g').attr('stroke', '#e5e7eb').selectAll('line')
        .data(edges).join('line').attr('stroke-width', 1.5)

      const node = svg.append('g').selectAll('g')
        .data(nodes).join('g')

      const circles = node.append('circle')
        .attr('r', 12)
        .attr('fill', d => color(d.mastery_score || 0))
        .attr('stroke', '#374151').attr('stroke-width', 0.8)
        .call(d3.drag()
          .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
          .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
          .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
        )

      node.append('title').text(d => `${d.name} (${(d.mastery_score*100).toFixed(0)}%)`)
      node.append('text')
        .text(d => d.name)
        .attr('x', 16).attr('y', 4)
        .attr('font-size', 10).attr('fill', '#111827')

      simulation.on('tick', () => {
        link
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y)
        node.attr('transform', d => `translate(${d.x},${d.y})`)
      })

      cleanup = () => simulation.stop()
    }
    if (userId && token) load()
    return () => { isMounted = false; cleanup() }
  }, [userId, token])

  return (
    <div className="border rounded-lg p-3 bg-white">
      <div className="text-sm text-gray-600 mb-2">Learner Knowledge Graph</div>
      <svg ref={svgRef} className="w-full h-[440px]"></svg>
    </div>
  )
}


