import { PageHeader } from "@/components/common/page-header";
import { ProductForm } from "@/components/products/product-form";

export default function ProductNewPage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="新建商品" description="填写基础信息，也可以直接粘贴商品链接或完整分享文案。" />
      <ProductForm submitLabel="创建商品" />
    </div>
  );
}
