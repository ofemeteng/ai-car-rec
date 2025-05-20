/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: "standalone",
  // async headers() {
  //   return [
  //     {
  //       source: "/(.*)", // Apply to all routes
  //       headers: [
  //         {
  //           key: "Access-Control-Allow-Origin",
  //           value: "*",
  //         },
  //         {
  //           key: "Access-Control-Allow-Methods",
  //           value: "GET, POST, PUT, DELETE, PATCH, OPTIONS",
  //         },
  //         {
  //           key: "Access-Control-Allow-Headers",
  //           value: "*",
  //         },
  //         {
  //           key: "Access-Control-Allow-Credentials",
  //           value: "true",
  //         },
  //         {
  //           key: "Access-Control-Max-Age",
  //           value: "86400", // cache preflight for 1 day
  //         },
  //         {
  //           key: "Cross-Origin-Embedder-Policy",
  //           value: "unsafe-none",
  //         },
  //         {
  //           key: "Cross-Origin-Opener-Policy",
  //           value: "unsafe-none",
  //         },
  //         {
  //           key: "Cross-Origin-Resource-Policy",
  //           value: "cross-origin",
  //         },
  //         {
  //           key: "Origin-Agent-Cluster",
  //           value: "?0",
  //         },
  //       ],
  //     },
  //   ];
  // },
};

export default nextConfig;


