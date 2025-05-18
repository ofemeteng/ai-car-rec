"use client";

import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  useCoAgent,
  useCoAgentStateRender,
} from "@copilotkit/react-core";
import { Progress } from "./Progress";
import { AgentState, Recommendation } from "@/lib/types";
import { useModelSelectorContext } from "@/lib/model-selector-provider";
import { RecommendationCard } from "./RecommendationCard";

export function RecommendationCanvas() {
  const { model, agent } = useModelSelectorContext();

  const { state, setState } = useCoAgent<AgentState>({
    name: agent,
    initialState: {
      model,
    },
  });

  useCoAgentStateRender({
    name: agent,
    render: ({ state, nodeName, status }) => {
      if (!state.logs || state.logs.length === 0) {
        return null;
      }
      return <Progress logs={state.logs} />;
    },
  });

  const recommendations: Recommendation[] = state.recommendations || [];

  return (
    <div className="w-full h-full overflow-y-auto p-10 bg-[#F5F8FF]">
      <div className="space-y-8 pb-10">
        {/* <div>
          <h2 className="text-lg font-medium mb-3 text-primary">
            Research Question
          </h2>
          <Input
            placeholder="Enter your research question"
            value={state.research_question || ""}
            onChange={(e) =>
              setState({ ...state, research_question: e.target.value })
            }
            aria-label="Research question"
            className="bg-background px-6 py-8 border-0 shadow-none rounded-xl text-md font-extralight focus-visible:ring-0 placeholder:text-slate-400"
          />
        </div> */}

        {/* Section to display RecommendationCards */}
        {recommendations.length > 0 && (
          <div>
            <h2 className="text-lg font-medium mb-4 text-primary">
              Recommendations
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((rec, index) => (
                <RecommendationCard
                  key={index} // rec.id || index  Use a unique id if available, otherwise index
                  recommendation={rec}
                  number={index + 1}
                  // You can add actions, onMouseEnter, onMouseLeave if needed
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

}
