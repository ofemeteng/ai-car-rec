// export type Resource = {
//   url: string;
//   title: string;
//   description: string;
// };

export type Recommendation = {
  car: string;
  tagline: string;
  content: string;
};

export type AgentState = {
  model: string;
  research_question: string;
  report: string;
  recommendations?: Recommendation[];
  // resources: any[];
  logs: any[];
}