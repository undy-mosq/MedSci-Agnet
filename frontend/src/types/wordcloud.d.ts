declare module 'wordcloud' {
  interface WordCloudOptions {
    list: [string, number][];
    gridSize?: number;
    weightFactor?: number | ((size: number) => number);
    fontFamily?: string;
    color?:
      | string
      | ((word: string, weight: string | number, fontSize: number, distance: number) => string);
    rotateRatio?: number;
    backgroundColor?: string;
  }

  function WordCloud(element: HTMLElement, options: WordCloudOptions): void;
  export default WordCloud;
}
