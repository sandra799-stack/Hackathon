import { NextResponse } from 'next/server';

export async function GET(request: Request, context: { params: { merchantId: string; promotionName: string } }) {
  // Extract merchantId and promotionName from context.params (await required in Next.js 15+)
  const { merchantId, promotionName } = await context.params;

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/delete-job/${merchantId}/${promotionName}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error deleting job: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in delete-job API route:', error);
    return NextResponse.json(
      { error: 'Failed to delete job' },
      { status: 500 }
    );
  }
}