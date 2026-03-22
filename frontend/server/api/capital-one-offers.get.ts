/**
 * AscendFi-curated overview of Capital One product lines (public marketing).
 * Images are stock photos (Unsplash) for illustration only—not Capital One creative assets.
 * Rates, bonuses, and approvals: always confirm on capitalone.com.
 */

function unsplash(photoId: string, w: number, h: number) {
  return `https://images.unsplash.com/${photoId}?ixlib=rb-4.0.3&auto=format&fit=crop&w=${w}&h=${h}&q=80`
}

export default defineEventHandler(() => {
  return {
    disclaimer:
      'AscendFi is not affiliated with Capital One. Product names are theirs; images are illustrative stock photos. All terms, APRs, fees, and approvals are only on Capital One’s website or app.',

    hero: {
      image: unsplash('photo-1563986768609-322da13575f3', 1600, 900),
      imageAlt: 'Person paying with a credit card at a café terminal',
      title: 'Capital One',
      subtitle: 'Cards, banking, and auto—what they offer',
    },

    ecosystem: [
      {
        id: 'creditwise',
        title: 'CreditWise',
        description: 'Free credit score monitoring and alerts. Checking your score through CreditWise does not hurt your credit.',
        url: 'https://www.capitalone.com/creditwise/',
        image: unsplash('photo-1554224155-6726b3ff858f', 800, 520),
        imageAlt: 'Desk with laptop, calculator, and financial planning notes',
      },
      {
        id: 'travel',
        title: 'Capital One Travel',
        description: 'Book flights, hotels, and cars in one place. Perks and earn rates depend on which card you carry.',
        url: 'https://www.capitalonetravel.com/',
        image: unsplash('photo-1488646953014-85cb44e25828', 800, 520),
        imageAlt: 'Travel planning with map and camera on a table',
      },
      {
        id: 'shopping',
        title: 'Capital One Shopping',
        description: 'Browser tools and deals to compare prices and find coupons—separate from your bank login.',
        url: 'https://capitaloneshopping.com/',
        image: unsplash('photo-1607082348824-0a96f2a4b9da', 800, 520),
        imageAlt: 'Online shopping with laptop and gift boxes',
      },
    ],

    categories: [
      {
        id: 'credit_cards_travel',
        title: 'Travel rewards cards',
        blurb:
          'Earn miles on purchases; premium cards add travel credits, lounge access, and extra value when you book through Capital One Travel. Compare annual fees to perks you will actually use.',
        hubUrl: 'https://www.capitalone.com/credit-cards/travel-rewards/',
        image: unsplash('photo-1436491865332-7a61a109cc05', 1200, 480),
        imageAlt: 'Commercial airplane flying above clouds',
        offers: [
          {
            id: 'venture-x',
            name: 'Venture X',
            pitch: 'Premium travel rewards: higher earn on travel booked through Capital One, annual travel credits, and lounge-style benefits on eligible products.',
            highlights: ['Welcome offers change—check the site', 'Annual fee in the premium tier', 'Strong fit for frequent travelers'],
            url: 'https://www.capitalone.com/credit-cards/venture-x-rewards-card/',
            image: unsplash('photo-1569154941061-e231b4725ef1', 720, 400),
            imageAlt: 'Airport lounge seating and windows',
          },
          {
            id: 'venture',
            name: 'Venture Rewards',
            pitch: 'Flat miles on everyday spending with flexible redemption toward travel.',
            highlights: ['Miles on every purchase', 'Redeem through Capital One Travel or other options per terms', 'Lower annual fee than Venture X'],
            url: 'https://www.capitalone.com/credit-cards/venture/',
            image: unsplash('photo-1527004013197-933c4bb611b3', 720, 400),
            imageAlt: 'City skyline at dusk',
          },
          {
            id: 'venture-one',
            name: 'VentureOne',
            pitch: 'Entry to the Venture family—often a $0 annual fee option with a lower earn rate.',
            highlights: ['Good first travel card', 'Intro APR may be available—read disclosures', 'Upgrade path as your profile improves'],
            url: 'https://www.capitalone.com/credit-cards/ventureone/',
            image: unsplash('photo-1464037866556-6812c9d1c72e', 720, 400),
            imageAlt: 'View from airplane window above clouds',
          },
        ],
      },
      {
        id: 'credit_cards_cash',
        title: 'Cash back & everyday rewards',
        blurb:
          'Simple flat-rate cash back or higher percentages on dining, groceries, streaming, and entertainment—pick the card that matches where your money already goes.',
        hubUrl: 'https://www.capitalone.com/credit-cards/cash-back/',
        image: unsplash('photo-1556742502-ec7c0e9f34b1', 1200, 480),
        imageAlt: 'Contactless payment with phone at a register',
        offers: [
          {
            id: 'quicksilver',
            name: 'Quicksilver',
            pitch: 'Straightforward unlimited cash back on every purchase—easy to understand and use.',
            highlights: ['Often ~1.5% on everything—verify current rate', 'Rotating welcome bonuses', 'Intro 0% APR promotions appear periodically'],
            url: 'https://www.capitalone.com/credit-cards/quicksilver/',
            image: unsplash('photo-1556742049-0cfed4f6a45d', 720, 400),
            imageAlt: 'Customer completing a card payment at checkout',
          },
          {
            id: 'savor',
            name: 'Savor & SavorOne',
            pitch: 'Extra cash back on dining, entertainment, streaming, and groceries on eligible versions.',
            highlights: ['Savor vs SavorOne: fee and earn rates differ', 'Great if dining out is a big line item', 'Read category definitions in the rewards terms'],
            url: 'https://www.capitalone.com/credit-cards/savorone-good-credit/',
            image: unsplash('photo-1517248135467-4c7edcad34c4', 720, 400),
            imageAlt: 'Busy restaurant interior with warm lighting',
          },
        ],
      },
      {
        id: 'credit_cards_build',
        title: 'Credit building & fair credit',
        blurb:
          'Secured, student, and no-frills options when you are starting out or rebuilding. On-time payments and low utilization matter more than rewards at this stage.',
        hubUrl: 'https://www.capitalone.com/credit-cards/build-credit/',
        image: unsplash('photo-1454165804606-c3d57bc86b40', 1200, 480),
        imageAlt: 'Hands reviewing documents and charts on a desk',
        offers: [
          {
            id: 'platinum',
            name: 'Platinum Mastercard',
            pitch: 'Focused on access and responsible use for fair-credit profiles—not a heavy rewards card.',
            highlights: ['Often $0 annual fee on eligible products', 'Automatic line reviews may apply', 'Keeps utilization visible on your report'],
            url: 'https://www.capitalone.com/credit-cards/platinum/',
            image: unsplash('photo-1543286386-713bdd548da4', 720, 400),
            imageAlt: 'Hand writing notes in a notebook',
          },
          {
            id: 'secured',
            name: 'Secured Card',
            pitch: 'A refundable deposit opens your line; consistent payments can help you graduate to unsecured.',
            highlights: ['Deposit size ties to credit limit', 'Reports like any other card', 'Graduation rules are in the official agreement'],
            url: 'https://www.capitalone.com/credit-cards/secured-mastercard/',
            image: unsplash('photo-1563013544-824ae1b704d3', 720, 400),
            imageAlt: 'Wallet with credit cards',
          },
        ],
      },
      {
        id: 'business',
        title: 'Small-business cards',
        blurb:
          'Spark and other business cards keep work spend separate, may offer employee cards, and mirror consumer-style cash back or miles.',
        hubUrl: 'https://www.capitalone.com/small-business/credit-cards/',
        image: unsplash('photo-1507679799987-c73779587ccf', 1200, 480),
        imageAlt: 'Professional adjusting tie in business attire',
        offers: [
          {
            id: 'spark',
            name: 'Spark cash & miles',
            pitch: 'Business rewards with tools that pair with bookkeeping on eligible products.',
            highlights: ['Business information required to apply', 'Employee cards on some products', 'Compare Spark variants for fee vs earn'],
            url: 'https://www.capitalone.com/small-business/credit-cards/',
            image: unsplash('photo-1497366216548-37526070297c', 720, 400),
            imageAlt: 'Bright open office with desks and windows',
          },
        ],
      },
      {
        id: 'banking',
        title: '360 checking & savings',
        blurb:
          'Online-first accounts: checking for daily spend, high-yield style savings, and CDs if you can lock funds. Compare live APY and ATM networks on their site.',
        hubUrl: 'https://www.capitalone.com/bank/',
        image: unsplash('photo-1579621970563-ebec7560ff3e', 1200, 480),
        imageAlt: 'Coins stacked in front of a small plant—savings concept',
        offers: [
          {
            id: '360-checking',
            name: '360 Checking',
            pitch: 'Spending account with debit card; fee-free ATMs on participating networks.',
            highlights: ['Often no minimum balance for retail versions', 'Early direct deposit where available', 'Review overdraft and fee schedule'],
            url: 'https://www.capitalone.com/checking-account/online-checking-account/',
            image: unsplash('photo-1563986768494-4dee2763ff3f', 720, 400),
            imageAlt: 'Debit card on a keyboard',
          },
          {
            id: '360-savings',
            name: '360 Performance Savings',
            pitch: 'Savings with a competitive APY that moves with the rate environment.',
            highlights: ['FDIC insurance limits apply', 'Savings goals in the app', 'Compare to CD rates if you will not need the cash soon'],
            url: 'https://www.capitalone.com/bank/savings-accounts/online-performance-savings/',
            image: unsplash('photo-1579621970795-87facc2f976d', 720, 400),
            imageAlt: 'Piggy bank and coins on wood surface',
          },
          {
            id: 'cds',
            name: 'Certificates of deposit',
            pitch: 'Lock a rate for a fixed term; useful when you have a clear timeline and do not need instant access.',
            highlights: ['Early withdrawal penalties', 'Ladder multiple CDs for flexibility', 'Compare term lengths to your goals'],
            url: 'https://www.capitalone.com/bank/cd-accounts/',
            image: unsplash('photo-1551288049-bebda4e38f71', 720, 400),
            imageAlt: 'Laptop showing analytics and charts',
          },
        ],
      },
      {
        id: 'auto',
        title: 'Auto financing',
        blurb:
          'Pre-qualification and refinancing through Auto Navigator and related flows. Final rate and payment depend on the vehicle, term, and your credit.',
        hubUrl: 'https://www.capitalone.com/auto-financing/',
        image: unsplash('photo-1492144534655-ae79c964c9d7', 1200, 480),
        imageAlt: 'Sports car on an open road',
        offers: [
          {
            id: 'auto-navigator',
            name: 'Auto Navigator',
            pitch: 'See financing estimates while you shop inventory—then finish at a participating dealer.',
            highlights: ['Pre-qualification is not a final approval', 'Compare total interest, not only monthly payment', 'Refinancing may lower rate if your credit improved'],
            url: 'https://www.capitalone.com/auto-financing/',
            image: unsplash('photo-1583121274602-3e2820c69888', 720, 400),
            imageAlt: 'Rows of cars at a dealership lot',
          },
        ],
      },
    ],
  }
})
