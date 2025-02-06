
const d3Cloud = require('d3-cloud');
import React, { useEffect, useState, useRef, useMemo } from 'react';
import * as d3 from 'd3';
import { useGlobalSearchContext } from '../../../../../contexts/searchContext';
import { useGlobalTabContext } from '../../../../../contexts/tabContext';

const useResizeObserver = (ref: any) => {
  const [dimensions, setDimensions] = useState(
    { bottom: 0, height: 0, left: 0, right: 0, top: 0, width: 0, x: 0, y: 0 });
  useEffect(() => {
    const observeTarget = ref.current;
    const resizeObserver = new ResizeObserver((entries) => {
      entries.forEach(entry => {
        setDimensions(entry.contentRect);
      });
    });
    resizeObserver.observe(observeTarget);
    return () => {
      resizeObserver.unobserve(observeTarget);
    }
  }, [ref]);
  return dimensions;
};


interface WordCloudProps {
  data: Array<{ text: string, size: number }>;
  author? : boolean;
}

// class for drawing a wordcloud
const WordCloud: React.FC<WordCloudProps> = ({ data, author }) => {
  if (!data.length) {
    return null;
  }

  // responsive Design
  const containerRef = React.useRef<SVGSVGElement>(null);
  const wrapperRef = useRef(null);
  const dimension = useResizeObserver(wrapperRef);

  // search for word
  const { tab, setTab } = useGlobalTabContext()
  const { setQuery } = useGlobalSearchContext()

  // resize the fontsize to the width and height
  const resize = () => {
    const maxSize = d3.max(data, d => d.size) as number;
    let scale = Math.max(dimension.height, dimension.width) / 8 / maxSize;
    const words_div = data
      // display fontsize min 
      .filter(word => word.size * scale >= 10)
      .map((word: any) => ({ ...word, size: word.size * scale }));
    return words_div
  }

  // clickable words for search, interactive
  const handleClick = (word: any) => {
    const w = word.target.textContent
    const current = tab
    setQuery(w)
    setTab('search')
  };

  // hover to enlarge font size, interactive
  const handleHover = (word: any) => {
    d3.select(word.target)
      .raise()
      .transition()
      .duration(300)
      .style('font-size', (d: any) => `${d.size + 15}px`);
  };

  // hover out the word to have normal font size, interactive
  const handleMouseOut = (word: any) => {
    d3.select(word.target)
      .transition()
      .duration(300)
      .style('font-size', (d: any) => `${d.size}px`);
  };

  // prepare words for the WordCloud, only changed if data or dimensions changes
  const words = useMemo(() => resize(), [data, dimension])

  // draw the WordCloud, if the words changes
  React.useEffect(() => {

    // Element for Responsive Design
    const svg = d3.select(containerRef.current);

    let dimensions = {
      width: dimension.width,
      height: dimension.height,
    };

    svg
      .classed("wordcloud-svg", true)
      .attr("width", dimensions.width)
      .attr("height", dimensions.height)

    // clear everything on refresh
    const everything = svg.selectAll("*");
    everything.remove();

    // draw the Layout for the wordcloud
    const layout = d3Cloud()
      .size([dimensions.width, dimensions.height])
      .words(words)
      .padding(0)
      .rotate(() => 0)
      .font('Impact')
      .fontSize((d: any) => d.size)
      .on('end', draw);
    layout.start();

    // draw the words 
    function draw(words: any) {
      d3.select(containerRef.current)
        .append('g')
        .attr('transform', `translate(${dimensions.width / 2},${dimensions.height / 2})`)
        .selectAll('text')
        .data(words)
        .enter().append('text')
        .style('font-size', (d: any) => `${d.size}px`)
        .style('font-family', 'Impact')
        .style('fill', (d, i) => d3.schemeCategory10[i % 10])
        .style('cursor', 'pointer')
        .attr('text-anchor', 'middle')
        .attr('transform', (d: any) => `translate(${[d.x, d.y]})rotate(${d.rotate})`)
        .text((d: any) => d.text)
        .on('click', (d: any) => handleClick(d))
        .on('mouseover', (d: any) => handleHover(d))
        .on('mouseout', (d: any) => handleMouseOut(d));
    }
  }, [words]);

  // if wordcloud_author is using the component, we need to adjust the class for CSS
  const  wcAuthorDiv = (author) ? "h-[43.3vh]" : "h-[60vh] md:h-[80vh] xl:h-[60vh]";

  return (
    <div ref={wrapperRef} className={wcAuthorDiv}>

      <svg ref={containerRef} style={{ overflow: 'visible' }} />
     
    </div>
  );
};

export default WordCloud
