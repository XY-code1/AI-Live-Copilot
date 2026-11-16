import { PageHeader } from "@/components/common/page-header";
import { ProductForm } from "@/components/products/product-form";

export default function ProductNewPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="新建商品" description="手动创建商品基础信息。" />
      <ProductForm submitLabel="创建商品" />
    </div>
  );
}
