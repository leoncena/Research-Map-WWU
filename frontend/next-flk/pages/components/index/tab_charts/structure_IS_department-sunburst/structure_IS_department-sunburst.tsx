//Copyright 2018–2020 Observable, Inc.
//Permission to use, copy, modify, and/or distribute this software for any
//purpose with or without fee is hereby granted, provided that the above
//copyright notice and this permission notice appear in all copies.

import React, { useRef, useEffect, useState } from 'react'
import * as d3 from 'd3'
import PublicationContextSetter from './publicationContextSetter'

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

export type DataType = { x0: number; x1: number; y0: number; y1: number }

//export type HierarchyType = { name:any, x0:number, x1: number, y0:number, y1:number, loc:number, id:any, current:any, target:any }

function StructureISSunburst({ Data }: any) {
  //DOM Element References
  const svgRef = useRef(null)
  const tooltipRef = useRef(null)
  //Referencing Div Element with Resize Observer
  const wrapperRef = useRef(null)
  const dimension = useResizeObserver(wrapperRef)

  // useState Hook for setting and accessing the publicationId of last clicked publication
  const [publicationId, setPublicationId] = useState('none')
  const [letzteEbene, setLetzteEbene] = useState(false)

  useEffect(() => {
    const svg = d3.select(svgRef.current)
    if (!dimension) return

    //Data
    const dataset = Data

    //Dimensions
    let dimensions = {
      width: dimension.width,
      height: dimension.height,
      margins: 20,
      radius: 0,
    }

    //calculate Radius
    dimensions.radius = dimensions.width / 6

    //select created SVG element
    svg
      .classed('sunburst-svg', true)
      .attr('viewBox', [0, 0, dimensions.width, dimensions.width])
      .attr('width', dimensions.width)
      .attr('height', dimensions.height)
      .attr('text-anchor', 'middle')

    //Clear everything on refresh
    const everything = svg.selectAll('*')
    everything.remove()

    //Append group for all path elements of Sunburst Chart
    const container = svg
      .append('g')
      .classed('sunburst-container', true)
      .attr(
        'transform',
        `translate(${dimensions.width / 2},${dimensions.width / 2})`
      )

    //Data modifications (Hierarchy, Value for each arc, sort)
    const root = d3.hierarchy(dataset)

    const value = (d: { loc: number }) => d.loc
    value == null ? root.count() : root.sum((d) => Math.max(0, value(d)))
    root.sort((a, b) => d3.descending(a.value, b.value))

    //partition layout for Sunburst
    d3.partition().size([2 * Math.PI, root.height + 1])(root)
    root.each((d: any) => (d.current = d))

    // construct color scale
    const fill = '#ccc'
    const fillOpacity = 0.6
    const color = d3.scaleOrdinal(
      d3.quantize(d3.interpolateRainbow, dataset.children.length + 1)
    )

    // Construct arc generator.
    const arc = d3
      .arc<DataType>()
      .startAngle((d) => d.x0)
      .endAngle((d) => d.x1)
      .padAngle((d) => Math.min((d.x1 - d.x0) / 2, 0.01))
      .padRadius(dimensions.radius * 1.5)
      .innerRadius((d) => d.y0 * dimensions.radius)
      .outerRadius((d) =>
        Math.max(d.y0 * dimensions.radius, d.y1 * dimensions.radius - 1)
      )

    //Draw all paths of Sunburst to the group
    const path = container
      .append('g')
      .selectAll('path')
      .data(root.descendants().slice(1))
      .join('path')
      .classed('sunburst-arc', true)
      .attr('fill', (d) => {
        //@ts-ignore
        while (d.depth > 1) d = d.parent
        return color(d.data.name)
      })
      .attr('fill-opacity', (d: any) =>
        arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0
      )
      .attr('pointer-events', (d: any) =>
        arcVisible(d.current) ? 'auto' : 'none'
      )
      .attr('d', (d: any) => arc(d.current))

    //Zoom function on each children
    path
      .filter((d: any) => d.children)
      .style('cursor', 'pointer')
      //@ts-ignore
      .on('click', clicked)

    //Get data of last hierarchy element -> get data of publications
    path
      .filter((d) => !d.children)
      .style('cursor', 'pointer')
      .on('click', function (event, i) {
        setPublicationId(i.data.id)
        setLetzteEbene(true)
      })

    //Style Tooltip
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

    //Tooltip on mouseover
    path.on('mouseover', (event, value) => {
      tooltip.style('display', 'block')
      tooltip.append('text').text(value.data.name)
    })
    //Tooltip on mousemove
    path.on('mousemove', (event) => {
      tooltip.style('top', `${event.pageY}px`)
      tooltip.style('right', 'initial')
      tooltip.style('left', `${event.pageX}px`)
      tooltip.style('bottom', 'initial')
    })
    //Tooltip on mouseleave
    path.on('mouseleave', (event) => {
      tooltip.style('display', 'none')
      tooltip.selectAll('text').remove()
    })

    //Labels on Sunburst Arcs
    const label = container
      .append('g')
      .attr('pointer-events', 'none')
      .attr('text-anchor', 'middle')
      .style('user-select', 'none')
      .selectAll('text')
      .data(root.descendants().slice(1))
      .join('text')
      .attr('dy', '0.35em')
      .attr('fill-opacity', (d: any) => +labelVisible(d.current))
      .attr('transform', (d: any) => labelTransform(d.current))
      .text((d: any) => d.data.name.slice(0, 20))

    //Appending Middle Circle for zoom back
    const parent = container
      .append('circle')
      .datum(root)
      .attr('r', dimensions.radius)
      .attr('fill', 'none')
      .attr('pointer-events', 'all')
      //@ts-ignore
      .on('click', clicked)

    //Zoom Function
    function clicked(
      event: any,
      p: { parent: any; x0: number; x1: number; depth: number }
    ) {
      //Parent Element in circle
      parent.datum(p.parent || root)

      root.each(
        (d: any) =>
          (d.target = {
            x0:
              Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) *
              2 *
              Math.PI,
            x1:
              Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) *
              2 *
              Math.PI,
            y0: Math.max(0, d.y0 - p.depth),
            y1: Math.max(0, d.y1 - p.depth),
          })
      )

      const t = container.transition().duration(750)

      // Transition the data on all arcs, even the ones that aren’t visible,
      // so that if this transition is interrupted, entering arcs will start
      // the next transition from the desired position.

      path
        //@ts-ignore
        .transition(t)
        .tween('data', (d: any) => {
          const i = d3.interpolate(d.current, d.target)
          return (t: any) => (d.current = i(t))
        })
        //@ts-ignore
        .filter(function (d) {
          //@ts-ignore
          return +this.getAttribute('fill-opacity') || arcVisible(d.target)
        })
        //@ts-ignore
        .attr('fill-opacity', (d: any) =>
          arcVisible(d.target) ? (d.children ? 0.6 : 0.4) : 0
        )
        //@ts-ignore
        .attr('pointer-events', (d: any) =>
          arcVisible(d.target) ? 'auto' : 'none'
        )
        //@ts-ignore
        .attrTween('d', (d: any) => () => arc(d.current))

      label
        //@ts-ignore
        .filter(function (d) {
          //@ts-ignore
          return +this.getAttribute('fill-opacity') || labelVisible(d.target)
        })
        //@ts-ignore
        .transition(t)
        .attr('fill-opacity', (d: any) => +labelVisible(d.target))
        .attrTween('transform', (d: any) => () => labelTransform(d.current))
      //}
    }

    //Calculate if arc pieces are visible or not
    function arcVisible(d: { y1: number; y0: number; x1: number; x0: number }) {
      return d.y1 <= 3 && d.y0 >= 1 && d.x1 > d.x0
    }

    //Calculate if labels are visible or not
    function labelVisible(d: {
      y1: number
      y0: number
      x1: number
      x0: number
    }) {
      return d.y1 <= 3 && d.y0 >= 1 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.03
    }

    //Transform Labels when zooming in
    function labelTransform(d: { x0: any; x1: any; y0: any; y1: any }) {
      const x = (((d.x0 + d.x1) / 2) * 180) / Math.PI
      const y = ((d.y0 + d.y1) / 2) * dimensions.radius
      return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`
    }
  }, [Data, dimension]) //redraw chart if data or dimensions change

  return (
    <div ref={wrapperRef} className="h-[60vh] md:h-[80vh] xl:h-[60vh]">
      <div ref={tooltipRef} />
      <svg ref={svgRef} />
      {letzteEbene ? (
        <PublicationContextSetter publicationId={publicationId} />
      ) : null}
    </div>
  )
}

export default StructureISSunburst
