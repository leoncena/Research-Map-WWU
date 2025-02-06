import React from 'react';
import { Slider } from '@mui/material';

interface WCA_SliderProps {
    min: number;
    max: number;
    onChange: (value: number) => void;
}

// class for an React slider
const Wordcloud_author_slider: React.FC<WCA_SliderProps> = ({ min, max, onChange }) => {
    const marks = [
        { value: min, label: `${min}` },
        { value: max, label: `${max}` },
      ];
    return (
        <div className= "flex flex-row justify-center">
        <Slider
            aria-label="filterYear"
            defaultValue={max}
            valueLabelDisplay="auto"
            step={1}
            marks = {marks}
            min={min}
            max={max}
            size={"small"}
            sx={{ width: 200 }}
            getAriaValueText={(value) => `${value}`}
            track="inverted"
            onChangeCommitted={(e,newVal) => onChange(newVal as number)}
        />
        </div>
    );
};

export default Wordcloud_author_slider;
