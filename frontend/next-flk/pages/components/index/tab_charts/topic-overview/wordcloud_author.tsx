import React, { useState, useMemo } from 'react';
import WordCloud from './wordcloud_maincomponent';
import * as d3 from 'd3';
import Wordcloud_author_slider from './wordcloud_author_slider';

interface Wordcloud_author_props {
  dataInput: [{
    _id: any,
    author_id: number,
    publications:
    Array<{
      id: number,
      data_for_wordcloud: string
      publYear: number,
    }>
  }];
}

// class for drawing a wordcloud with interactive slider
const Wordcloud_author: React.FC<Wordcloud_author_props> = ({ dataInput }) => {
  if (!dataInput.length) {
    return null;
  }

  // extract relevant data
  const data = dataInput[0].publications

  // slider input, does not show if only one year in data
  const minYear = d3.min(data, d => d.publYear) as number;
  const maxYear = d3.max(data, d => d.publYear) as number;
  const [dataYear, setDataYear] = useState(maxYear || 0);
  const showSlider = minYear !== maxYear;

  // selected data of the selected year
  const [selectedData, setSelectedData] = useState(data);

  // filter the data by selected year
  React.useEffect(() => {
    setSelectedData(
      data.filter(data => data.publYear >= dataYear)
    );

  }, [dataYear]);

  // funtion for preparing the data for the wordcloud by counting each word for selected data
  function countWords(data: Array<{
    id: number,
    data_for_wordcloud: string,
    publYear: number,
  }>) {
    const countedWords: { [key: string]: number } = {};
    data.forEach((data) => {
      const words = data.data_for_wordcloud.split(',');
      words.forEach((word) => {
        if (countedWords[word]) {
          countedWords[word] += 1;
        } else {
          countedWords[word] = 1;
        }
      });
    });

    // format the data for the input in wordcloud_maincomponent
    const countedWordsArray = Object.entries(countedWords)
      .map(([text, size]) => ({
        text: text as string,
        size: size as number,
      }));
    return countedWordsArray;
  }

  // if the selected Year changes the Data, the data are prepared for the wordcloud
  const worddata = useMemo(() => countWords(selectedData), [selectedData])

  return (
    <>
    
      {showSlider && (
        <Wordcloud_author_slider
          min={minYear}
          max={maxYear}
          onChange={(value: number) => setDataYear(value)}
        />)}
      
      <WordCloud data={worddata} author = {true}/>
    
    </>
  );
};

export default Wordcloud_author;
