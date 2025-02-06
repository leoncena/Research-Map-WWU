import { ResponsiveBar } from '@nivo/bar'
import React from 'react'

const ResearchOutputBarchart = ({ Data }: any) => (
  <ResponsiveBar
    data={Data}
    //Keys of stacked bars
    keys={[
      'Wirtschaftsinformatik und Informationsmanagement (Prof. Becker)',
      'Wirtschaftsinformatik und Interorganisationssysteme (Prof. Klein)',
      'Wirtschaftsinformatik, insbesondere IT-Sicherheit (Prof. B\u00f6hme)',
      'Quantitative Methoden in der Logistik (Dr. Meisel)',
      'Praktische Informatik in der Wirtschaft (Prof. Kuchen)',
      'Wirtschaftsinformatik, insb. IT-Sicherheit (Prof. Fischer)',
      'Informatik (Prof. Vossen)',
      'Wirtschaftsinformatik und Logistik (Prof. Hellingrath)',
      'Statistik und Optimierung (Prof. Trautmann)',
      'Forschungsgruppe Kommunikations- und Kollaborationsmanagement',
      'Quantitative Methoden der Wirtschaftsinformatik (Prof. M\u00fcller-Funk)',
      'Institut f\u00fcr Wirtschaftsinformatik - Mathematik f\u00fcr Wirtschaftswissenschaftler',
      'Lehrstuhl f\u00fcr Wirtschaftsinformatik und Controlling',
      'Professur f\u00fcr Maschinelles Lernen und Data Engineering (Prof. Gieseke)',
      'IT-Sicherheit (Prof. Hupperich)',
      'Digitale Transformation und Gesellschaft (Prof. Berger)',
      'Digitale Innovation und der \u00f6ffentliche Sektor (Prof. Brandt)',
    ]}
    indexBy="Jahr"
    margin={{ top: 40, right: 40, bottom: 80, left: 80 }}
    padding={0.3}
    valueScale={{ type: 'linear' }}
    //Rainbow Color Theme (like Sunburst)
    colors={[
      '#6E40AA',
      '#A03DB3',
      '#B93EAD',
      '#D23EA7',
      '#E64399',
      '#F9488A',
      '#FF5E63',
      '#FF6F52',
      '#FF7F41',
      '#F79338',
      '#EFA72F',
      '#CDCF37',
      '#73F65A',
      '#80F769',
      '#8CF877',
      '#96F983',
      '#B1FAA1',
      '#B8FAAA',
    ]}
    borderColor={{
      from: 'color',
      modifiers: [['darker', 1.6]],
    }}
    axisTop={null}
    axisRight={null}
    //x-Axis
    axisBottom={{
      tickSize: 5,
      tickPadding: 5,
      tickRotation: 0,
      legend: 'year',
      legendPosition: 'middle',
      legendOffset: 32,
      tickValues: [1990, 1995, 2000, 2005, 2010, 2015, 2020],
    }}
    //y-Axis
    axisLeft={{
      tickSize: 5,
      tickPadding: 5,
      tickRotation: 0,
      legend: 'number of publications',
      legendPosition: 'middle',
      legendOffset: -40,
    }}
    labelSkipWidth={12}
    labelSkipHeight={12}
    labelTextColor={{
      from: 'color',
      modifiers: [['darker', 1.6]],
    }}
    role="application"
    ariaLabel="Research Output"
  />
)

export default ResearchOutputBarchart
