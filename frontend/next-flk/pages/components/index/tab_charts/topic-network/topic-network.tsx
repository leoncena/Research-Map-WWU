import React, { useRef, useEffect, useState } from 'react'
import * as d3 from 'd3'
import { useGlobalTabContext } from '../../../../../contexts/tabContext'
import { useGlobalTabPrevContext } from '../../../../../contexts/tabPrevContext'
import { useGlobalSearchContext } from '../../../../../contexts/searchContext'

//Resize Observer tracking dimensions changes in Div Elements to resize chart accordingly to new dimensions
const useResizeObserver = (ref: any) => {
  const [dimensions, setDimensions] = useState({
    bottom: 0,
    height: 0,
    left: 0,
    right: 0,
    top: 0,
    width: 0,
    x: 0,
    y: 0,
  })
  useEffect(() => {
    const observeTarget = ref.current
    const resizeObserver = new ResizeObserver((entries) => {
      entries.forEach((entry) => {
        setDimensions(entry.contentRect)
      })
    })
    resizeObserver.observe(observeTarget)
    return () => {
      resizeObserver.unobserve(observeTarget)
    }
  }, [ref])
  return dimensions
}

function TopicNetwork({ Data }: any) {
  //DOM Element References
  const canvasRef = useRef(null)
  const tooltipRef = useRef(null)
  //Referencing Div Element with Resize Observer
  const wrapperRef = useRef(null)
  const dimension = useResizeObserver(wrapperRef)

  //Constants for State-Management
  const { tab, setTab } = useGlobalTabContext()
  const { tabPrev, setTabPrev } = useGlobalTabPrevContext()
  const { setQuery } = useGlobalSearchContext()

  useEffect(() => {
    const dataset = Data

    let dimensions = {
      width: dimension.width,
      height: dimension.height,
    }

    //Prepare Canvas for Visualization
    const canvas = canvasRef.current
    //@ts-ignore
    canvas.width = dimensions.width //* dpi;
    //@ts-ignore
    canvas.height = dimensions.height // * dpi;
    //@ts-ignore
    const context = canvas.getContext('2d')

    //Data Modification
    const nodes = dataset.nodes.map((d: any) => d)
    const edges = dataset.links.map((d: any) => d)

    //Color scheme for each nodes group
    const groups = dataset.nodes.map((d: any) => d.group)
    const color = d3.scaleOrdinal(groups, d3.schemeTableau10)

    //Force Layout to position nodes on canvas
    const simulation = d3
      .forceSimulation(nodes)
      .force(
        'center',
        d3.forceCenter(dimensions.width / 2, dimensions.height / 2)
      )
      .force(
        'link',
        d3
          .forceLink(edges)
          .id((d: any) => d.id)
          .strength((d: any) => d.value)
      )
      .force('charge', d3.forceManyBody().strength(-500)) //.strength(-100))
      .force('collide', d3.forceCollide())
      .velocityDecay(0.6)
      .on('tick', drawChart)

    //Current zoom state of canvas
    let transform = d3.zoomIdentity

    function drawChart() {
      //Initiate Canvas for drawing with current zoom state
      context.save()
      context.clearRect(0, 0, dimensions.width, dimensions.height)
      context.translate(transform.x, transform.y)
      context.scale(transform.k, transform.k)

      //Draw all Edges
      edges.forEach(function (d: {
        source: { x: any; y: any }
        target: { x: any; y: any }
      }) {
        context.beginPath()
        context.moveTo(d.source.x, d.source.y)
        context.lineTo(d.target.x, d.target.y)
        context.lineWidth = 0.5
        context.strokeStyle = '#aaa'
        context.stroke()
      })

      //Draw all Nodes
      nodes.forEach(function (d: {
        x: number
        y: any
        group: { toString(): string }
      }) {
        context.beginPath()
        context.moveTo(d.x + 5, d.y)
        context.arc(d.x, d.y, 10, 0, 2 * Math.PI)
        context.fillStyle = color(d.group)
        context.fill()
      })

      //Draw all Labels
      nodes.forEach((d: any) => {
        context.fillStyle = 'black'
        context.textAlign = 'center'
        context.font = '10px sans-serif'
        context.fillText(d.id, d.x, d.y + 20)
      })
      context.restore()
    }

    //OnClick handler for nodes
    //switch to search tab and search keyword of clicked node
    d3.select(canvas).on('click', (event) => {
      const x = event.offsetX
      const y = event.offsetY
      const zx = transform.invertX(x)
      const zy = transform.invertY(y)

      const foundNode: any = simulation.find(zx, zy, 10)

      if (foundNode) {
        setQuery(foundNode.id)
        setTabPrev(tab)
        setTab('search')
      }
    })

    //Tooltip Styling
    const tooltip = d3.select(tooltipRef.current).classed('div-tooltip', true)
    tooltip
      .style('position', 'absolute')
      .style('display', 'none')
      .style('border-radius', '4px')
      .style('padding', '8px 12px')
      .style('font-family', 'sans-serif')
      .style('font-size', '16px')
      .style('color', '#333')
      .style('background-color', '#fff')
      .style('pointer-events', 'none')
      .style('z-index', '1')
      .style('border', '0.5px solid #333')

    //Tooltip Positioning for hovering over nodes
    d3.select(canvas).on('mousemove', (event) => {
      const x = event.offsetX
      const y = event.offsetY
      const zx = transform.invertX(x)
      const zy = transform.invertY(y)

      tooltip.style('display', 'none')
      tooltip.selectAll('text').remove()

      const foundNode: any = simulation.find(zx, zy, 10)

      if (foundNode) {
        tooltip.style('top', `${event.pageY}px`)
        tooltip.style('right', 'initial')
        tooltip.style('left', `${event.pageX}px`)
        tooltip.style('bottom', 'initial')
        tooltip.style('display', 'block')
        tooltip.append('text').text(foundNode.id)
      }
    })

    //Zoom Functionality on Canvas
    d3.select(canvas).call(
      //@ts-ignore
      d3
        .zoom()
        .scaleExtent([0.05, 8])
        //.scaleExtent([0.1,8])
        .on('zoom', (event, value) => zoomed(event, value))
    )

    function zoomed(event: { transform: d3.ZoomTransform }, value: unknown) {
      transform = event.transform
      drawChart()
    }
  }, [Data, dimension]) //redraw chart if data or dimensions change

  return (
    <div ref={wrapperRef} className="h-[60vh] md:h-[80vh] xl:h-[60vh]">
      <div ref={tooltipRef} />
      <canvas id="canvas" ref={canvasRef}></canvas>
    </div>
  )
}

export default TopicNetwork
