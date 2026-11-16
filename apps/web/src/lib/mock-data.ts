import type {
  Asset,
  Comparison,
  Competitor,
  Product,
  Script,
  Task,
  Workspace,
} from "@/types";

export const currentWorkspace: Workspace = {
  id: "ws-1",
  name: "旅游直播团队",
  plan: "试用版",
};

export const products: Product[] = [
  {
    id: "p-1",
    name: "川西五日游",
    category: "旅游线路",
    summary: "成都出发，覆盖稻城亚丁、四姑娘山，小团出行。",
    price: 3280,
    currency: "CNY",
    status: "ready",
    createdAt: "2026-11-10T09:00:00Z",
    updatedAt: "2026-11-15T12:00:00Z",
    attributes: [
      {
        id: "a-1",
        label: "出行天数",
        value: "5 天 4 晚",
        status: "confirmed",
        sourceId: "s-1",
      },
      {
        id: "a-2",
        label: "出行方式",
        value: "小团（12 人以内）",
        status: "confirmed",
        sourceId: "s-1",
      },
      {
        id: "a-3",
        label: "购物安排",
        value: "待确认",
        status: "unconfirmed",
      },
      {
        id: "a-4",
        label: "费用包含",
        value: "部分已确认（住宿、门票）",
        status: "doubtful",
        sourceId: "s-1",
      },
    ],
    sources: [
      {
        id: "s-1",
        type: "pdf",
        name: "川西五日游行程单.pdf",
        reference: "第 2 页 · 行程安排",
        status: "ready",
        createdAt: "2026-11-10T09:00:00Z",
      },
      {
        id: "s-2",
        type: "image",
        name: "酒店现场图.png",
        status: "processing",
        createdAt: "2026-11-12T10:00:00Z",
      },
    ],
  },
  {
    id: "p-2",
    name: "云南大理丽江 6 日游",
    category: "旅游线路",
    summary: "大理古城、洱海、丽江古城，含接送机。",
    price: 2680,
    currency: "CNY",
    status: "draft",
    createdAt: "2026-11-13T14:00:00Z",
    updatedAt: "2026-11-14T09:00:00Z",
    attributes: [
      {
        id: "a-5",
        label: "出行天数",
        value: "6 天 5 晚",
        status: "confirmed",
        sourceId: "s-3",
      },
      {
        id: "a-6",
        label: "接送机",
        value: "含",
        status: "confirmed",
        sourceId: "s-3",
      },
    ],
    sources: [
      {
        id: "s-3",
        type: "url",
        name: "商品详情页",
        reference: "huodong.ctrip.com",
        status: "ready",
        createdAt: "2026-11-13T14:00:00Z",
      },
    ],
  },
];

export const competitors: Competitor[] = [
  {
    id: "c-1",
    productName: "川西五日游 · 经典版",
    brand: "某旅行社",
    price: 3580,
    notes: "同类线路，价格略高",
  },
];

export const comparisons: Comparison[] = [
  {
    id: "cmp-1",
    productId: "p-1",
    competitorId: "c-1",
    status: "ready",
    missingInfo: ["购物安排", "自费项目"],
    createdAt: "2026-11-15T13:00:00Z",
    differences: [
      {
        id: "d-1",
        field: "价格",
        ours: "¥3280",
        theirs: "¥3580",
        evidenceType: "source",
        side: "ours",
      },
      {
        id: "d-2",
        field: "出行方式",
        ours: "小团（12 人以内）",
        theirs: "大团（30 人）",
        evidenceType: "source",
        side: "ours",
      },
      {
        id: "d-3",
        field: "购物安排",
        ours: "待确认",
        theirs: "无购物",
        evidenceType: "speculative",
        side: "neutral",
      },
    ],
  },
];

export const scripts: Script[] = [
  {
    id: "sc-1",
    productId: "p-1",
    title: "川西五日游 · 首播话术",
    scenario: "日常带货",
    audience: "25-40 岁白领",
    style: "亲切自然",
    version: 1,
    status: "issue",
    createdAt: "2026-11-15T15:00:00Z",
    updatedAt: "2026-11-15T15:30:00Z",
    sections: [
      {
        id: "sec-1",
        kind: "opening",
        title: "开场吸引",
        content: "今天给大家带来一条川西 5 日游的线路，先把价格放在这里：3280 元。",
      },
      {
        id: "sec-2",
        kind: "selling_points",
        title: "核心卖点",
        content: "小团出行，12 人以内；住宿和门票都包含在费用里。",
      },
      {
        id: "sec-3",
        kind: "risk",
        title: "风险提示",
        content: "购物安排和自费项目暂时没有确认，下单前请咨询客服。",
      },
    ],
  },
];

export const assets: Asset[] = [
  {
    id: "as-1",
    kind: "analysis",
    name: "川西五日游 vs 经典版",
    productName: "川西五日游",
    updatedAt: "2026-11-15T13:00:00Z",
  },
  {
    id: "as-2",
    kind: "script",
    name: "川西五日游 · 首播话术",
    productName: "川西五日游",
    updatedAt: "2026-11-15T15:30:00Z",
  },
  {
    id: "as-3",
    kind: "source",
    name: "川西五日游行程单.pdf",
    productName: "川西五日游",
    updatedAt: "2026-11-10T09:00:00Z",
  },
];

export const recentTasks: Task[] = [
  {
    id: "t-1",
    name: "解析 川西五日游行程单.pdf",
    status: "done",
    createdAt: "2026-11-15T12:00:00Z",
  },
  {
    id: "t-2",
    name: "识别 酒店现场图.png",
    status: "running",
    createdAt: "2026-11-15T12:05:00Z",
  },
  {
    id: "t-3",
    name: "生成 首播话术",
    status: "pending",
    createdAt: "2026-11-15T12:10:00Z",
  },
];
