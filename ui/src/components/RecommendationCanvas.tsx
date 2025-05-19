"use client";

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

  const { state } = useCoAgent<AgentState>({
    name: agent,
    initialState: {
      model,
    },
  });

  // useCoAgentStateRender({
  //   name: agent,
  //   render: ({ state }) => {
  //     if (!state.logs || state.logs.length === 0) return null;
  //     return <Progress logs={state.logs} />;
  //   },
  // });

  try {
    useCoAgentStateRender({
      name: agent,
      render: ({ state }) => {
        const logs = state.logs ?? [];
        return <Progress logs={logs} />;
      },
    });
  } catch (err) {
    console.error("CopilotKit render error:", err);
  }
  

  const recommendations: Recommendation[] = state.recommendations || [];

  return (
    <div className="w-full h-full overflow-y-auto p-10 bg-[#F5F8FF]">
      <div className="space-y-8 pb-10">
        {recommendations.length > 0 && (
          <div>
            <h2 className="text-lg font-medium mb-4 text-primary">
              Recommendations
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((rec, index) => (
                <RecommendationCard
                  key={index}
                  recommendation={rec}
                  number={index + 1}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
