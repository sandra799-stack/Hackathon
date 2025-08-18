import { NextRequest, NextResponse } from 'next/server';

const allCategories = [
  { id: 1, title: 'Happy hour', description: 'Promote special drink offers during happy hours', tags: ['drinks', 'promotion', 'evening', 'bar'] },
  { id: 2, title: 'Birthdays', description: 'Celebrate customer birthdays with special offers', tags: ['celebration', 'personal', 'special', 'discount'] },
  { id: 3, title: 'Promocode depending on the weather', description: 'Weather-based promotional campaigns', tags: ['weather', 'dynamic', 'seasonal', 'promotion'] },
  { id: 4, title: 'Social media posts', description: 'Generate engaging social media content', tags: ['social', 'content', 'marketing', 'engagement'] },
  { id: 5, title: 'Know your consumer', description: 'Customer analytics and insights', tags: ['analytics', 'customer', 'insights', 'data'] },
  { id: 6, title: 'Recommend items to customers', description: 'Personalized product recommendations', tags: ['recommendation', 'personalization', 'products', 'ai'] }
];

function semanticSearch(query: string, categories: typeof allCategories) {
  if (!query.trim()) {
    return categories;
  }

  const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
  
  return categories.filter(category => {
    const searchableText = (
      category.title + ' ' + 
      category.description + ' ' + 
      category.tags.join(' ')
    ).toLowerCase();

    return searchTerms.some(term => 
      searchableText.includes(term) ||
      searchableText.split(' ').some(word => 
        word.includes(term) || term.includes(word)
      )
    );
  }).sort((a, b) => {
    const scoreA = calculateRelevanceScore(query, a);
    const scoreB = calculateRelevanceScore(query, b);
    return scoreB - scoreA;
  });
}

function calculateRelevanceScore(query: string, category: typeof allCategories[0]) {
  const searchTerms = query.toLowerCase().split(' ');
  let score = 0;

  searchTerms.forEach(term => {
    if (category.title.toLowerCase().includes(term)) {
      score += 10;
    }
    if (category.tags.some(tag => tag.toLowerCase().includes(term))) {
      score += 5;
    }
    if (category.description.toLowerCase().includes(term)) {
      score += 2;
    }
  });

  return score;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q') || '';

    const filteredCategories = semanticSearch(query, allCategories);

    return NextResponse.json({
      success: true,
      data: filteredCategories,
      total: filteredCategories.length,
      query: query
    });
  } catch (error) {
    console.error('Error fetching categories:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch categories' },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}