# Flow Lab Product Image Prompt System (2026-03-23)

## Purpose
This document converts the Flow Lab 9-image product template into a reusable image-generation system.

Goals:
- Keep the whole store visually consistent
- Preserve a premium light-office aesthetic
- Make future product-image production fast
- Give each product a ready-to-use image brief

Current products reviewed from `fl_products`:
- FL-001 `蒜了鴨`
- FL-003 `時來運轉沙漏`
- FL-004 `躺贏招財貓-躺贏`
- FL-005 `躺贏招財貓-閒樂`
- FL-006 `躺贏招財貓-躺賺`
- FL-007 `躺贏招財貓-到福`
- FL-008 `辦公室靜心解壓木魚`
- FL-009 `麻將捏捏樂創意解壓玩具`
- FL-010 `桌下抽屜式收納盒`

## Core Visual Direction

### Brand look
- Clean, bright, premium, Apple-like minimalism
- Shopee-friendly clarity, but not cheap marketplace clutter
- White, warm gray, pale wood, muted black typography
- One clear subject per image

### Base palette
- Background white: `#FFFFFF`
- Soft gray: `#F5F5F7`
- Warm light gray: `#EEE9E3`
- Text dark: `#1F1F1F`
- Secondary text: `#6E6A67`
- Accent only when needed: `#E96F2E`

### Typography direction
- Headline: bold sans-serif, large, clean
- Subtext: medium sans-serif
- Avoid decorative fonts, stickers, comic effects, loud gradients

### Universal negative prompt
Use this on every AI image generation request when applicable:

`low quality, blurry, noisy, oversaturated, cluttered background, cheap ecommerce style, excessive stickers, exaggerated shadows, distorted product shape, extra objects, duplicate product, warped hands, bad anatomy, wrong perspective, random text, watermark, logo corruption`

## The 9-Image System

### Image 1: Hero
Purpose:
- Stop scrolling
- State the main value immediately

Composition:
- Product centered
- Product occupies 60-70%
- White or `#F5F5F7` background
- Very little text

Text formula:
- `[Main benefit] | [Product name]`

Prompt scaffold:
- `premium ecommerce hero shot of [product], centered, isolated on a clean white or ultra-light gray background, soft studio lighting, subtle realistic shadow, minimal Apple-style composition, high-end office lifestyle brand aesthetic, square 1080x1080`

### Image 2: Before / After
Purpose:
- Show contrast
- Make the problem visible

Composition:
- Split scene or diagonal split
- Left side mess/problem
- Right side clean/improved state

Text formula:
- `Before | [pain]`
- `After | [benefit]`

Prompt scaffold:
- `split-scene ecommerce comparison for [product], left side cluttered stressful desk scene, right side clean focused minimal desk scene after using [product], premium realistic lighting, modern office mood, clear contrast, square composition`

### Image 3: Vibe Scene
Purpose:
- Sell the feeling
- Put the product into a premium life context

Composition:
- Product integrated into a premium desk scene
- No heavy labels

Universal vibe prompt:
- `minimal premium office desk scene, Apple-inspired styling, pale wood tabletop, soft natural side light, clean bright background, shallow depth of field, high-end lifestyle photography, realistic product placement, 8k`

### Image 4: Feature Breakdown
Purpose:
- Explain why the design is good

Composition:
- Product centered
- 3 to 4 thin callout lines
- Clean labels

Text formula:
- `[Feature]: [Benefit]`

Prompt scaffold:
- `technical feature breakdown board for [product], centered product on clean light background, thin callout lines, premium industrial design presentation, minimal infographic style, elegant ecommerce feature page, square layout`

### Image 5: Material Close-up
Purpose:
- Build trust
- Show texture and build quality

Composition:
- 70-80% close-up
- Focus on texture, edge, finish, touch point

Text formula:
- `看得見的細節 | [material / finish]`

Prompt scaffold:
- `macro close-up product photography of [product] material detail, premium texture, smooth edge finishing, soft studio lighting, luxury minimalist ecommerce style, ultra sharp surface detail`

### Image 6: Use Case
Purpose:
- Show usage
- Connect to focus / calm / efficiency

Composition:
- Human hand interaction if useful
- Leave top area for short text

Text formula:
- `為你的工作日常，找回專注心流`
- `在忙碌節奏中，留一點喘息空間`

Prompt scaffold:
- `realistic office use-case scene of [product], human interaction, premium minimalist desk, calm and productive mood, natural lighting, high-end brand photography, square ecommerce image`

### Image 7: SOP / Installation
Purpose:
- Lower usage resistance
- Reduce support questions

Composition:
- Three-step layout
- White background
- Icon + short captions

Text formula:
- `3 steps to use`
- `免釘安裝 / 輕鬆上手`

### Image 8: Dimensions
Purpose:
- Reduce return risk
- Clarify fit

Composition:
- Clean engineering-sheet style
- Front / side view
- Arrows and labels

Text formula:
- `精準尺寸，適配你的桌面場景`

### Image 9: Brand / Packaging / Guarantee
Purpose:
- Close the sale
- Reassure buyer

Composition:
- Reusable store-wide card
- Packaging + logo + promise + service notes

Content:
- `Flow Lab`
- `專注於質感與效率的輕生活選品`
- `台灣現貨`
- `24H 快速出貨`
- `完整售後服務`
- `七天鑑賞期`

## How To Use This System

For each product, you only need:
- Product name
- One core pain point or benefit
- 3 main features
- Material / texture description
- Real usage scenario
- Installation / usage steps if needed
- Product dimensions

Then generate:
- 3 mood-first images
- 3 trust/detail images
- 3 conversion images

## Product-by-Product Prompt Plans

---

## FL-010 桌下抽屜式收納盒

### Product positioning
- Role: 主力款
- Main value: free desk space, hide clutter, restore focus
- Best visual direction: clean desk organization

### Suggested text system
- Hero line: `釋放桌面空間 | 桌下抽屜式收納盒`
- Before/After pain: `桌面凌亂 → 工作更分心`
- Vibe line: `把雜亂收進視線之外`

### 3 key features
- Hidden under-desk design
- Smooth pull-out storage
- Large capacity for stationery and small tools

### Image-specific brief
1. Hero:
   - product isolated, elegant light gray background
2. Before/After:
   - messy cables and stationery vs clean minimal desk
3. Vibe:
   - pale wood desk, MacBook-style setup, product mounted below desk
4. Feature:
   - hidden installation / smooth slide / large capacity
5. Material:
   - matte ABS texture, rounded edge detail
6. Use case:
   - hand pulling drawer, storing pens and notes
7. SOP:
   - wipe / peel / stick
8. Dimensions:
   - front + side view with length, width, height, desk underside fit note
9. Brand closer:
   - universal Flow Lab card

---

## FL-009 麻將捏捏樂創意解壓玩具

### Product positioning
- Role: 引流款
- Main value: instant stress relief, desk toy, low-pressure purchase
- Best visual direction: playful but still premium

### Suggested text system
- Hero line: `釋放指尖壓力 | 麻將捏捏樂`
- Before/After pain: `手停不下來的焦躁 → 有出口的舒壓節奏`
- Vibe line: `忙裡偷閒，也可以很有質感`

### 3 key features
- soft squeeze feedback
- palm-size portability
- fun desk mood object

### Image-specific brief
1. Hero:
   - one clean piece on bright minimal background
2. Before/After:
   - stressed desk posture vs relaxed finger squeeze moment
3. Vibe:
   - minimal office desk with small playful object near keyboard
4. Feature:
   - portable / tactile / mood-lifting
5. Material:
   - surface and softness close-up
6. Use case:
   - fingers pressing while working
7. SOP:
   - take / squeeze / reset focus
8. Dimensions:
   - compact palm-size measurement
9. Brand closer:
   - universal card

---

## FL-008 辦公室靜心解壓木魚

### Product positioning
- Role: 引流款
- Main value: short reset ritual, desk calm, emotional decompression
- Best visual direction: zen office aesthetic

### Suggested text system
- Hero line: `找回片刻平靜 | 辦公室靜心解壓木魚`
- Before/After pain: `腦袋過載 → 節奏歸零`
- Vibe line: `在繁忙之中，留一個安靜按鈕`

### 3 key features
- calming ritual object
- compact desk-friendly size
- decorative and functional

### Image-specific brief
1. Hero:
   - wood object centered, calm white-gray background
2. Before/After:
   - overloaded work chaos vs quiet centered desk mood
3. Vibe:
   - sunlight, pale wood, minimal desk zen scene
4. Feature:
   - compact / decorative / calming
5. Material:
   - wood grain and rounded finish close-up
6. Use case:
   - hand lightly holding or using the object
7. SOP:
   - place / breathe / reset
8. Dimensions:
   - exact size for desktop fit
9. Brand closer:
   - universal card

---

## FL-004 to FL-007 躺贏招財貓系列

### Family suggestion
- Family name: `躺贏招財貓`
- Variants:
  - `躺贏`
  - `閒樂`
  - `躺賺`
  - `到福`

### Positioning
- Role: 引流款
- Main value: desk mood object, lucky charm, giftable collectible
- Best visual direction: cute premium small object, not childish cheap toy

### Shared text system
- Hero line: `替桌面加一點好運 | 躺贏招財貓`
- Before/After pain: `枯燥桌面 → 有記憶點的療癒角落`
- Vibe line: `有一點可愛，也有一點好運`

### Shared 3 key features
- decorative luck-themed desk object
- gifting-friendly collectible
- multiple variants for mood and style

### Variant note
The same 9-image system can be reused with:
- one shared family-wide structure
- one variant-specific hero image
- one variant comparison image if needed

### Best practice
- Make one `family` version for store consistency
- Then make one hero replacement per variant
- Optionally add one family comparison card:
  - `哪一款最適合你的桌面性格？`

---

## FL-003 時來運轉沙漏

### Product positioning
- Role: 毛利款
- Main value: premium desk decoration, time ritual, gift-worthy object
- Best visual direction: elegant, premium, slightly luxurious

### Suggested text system
- Hero line: `把時間變成桌面的風景 | 時來運轉沙漏`
- Before/After pain: `空白桌面缺少靈魂 → 更有質感的專注角落`
- Vibe line: `讓時間流動，也讓空間更安定`

### 3 key features
- premium decorative object
- calming motion
- gift-worthy presentation

### Image-specific brief
1. Hero:
   - premium centered object, soft shadow, luxury light
2. Before/After:
   - plain desk vs styled premium desk corner
3. Vibe:
   - elegant desk scene with sunlight and depth
4. Feature:
   - visual ritual / premium decor / gift mood
5. Material:
   - close-up glass, frame, fine texture
6. Use case:
   - hand turning the sand timer on a desk
7. SOP:
   - flip / place / enjoy
8. Dimensions:
   - exact size and desk fit
9. Brand closer:
   - universal card

---

## FL-002 桌面懸浮陀螺

### Product positioning
- Role: 毛利款
- Main value: premium desk conversation piece, kinetic decompression
- Best visual direction: futuristic minimalist

### Suggested text system
- Hero line: `讓桌面動起來 | 桌面懸浮陀螺`
- Before/After pain: `靜止而無聊的桌面 → 有節奏感的專注裝置`
- Vibe line: `科技感與療癒感，同時存在`

### 3 key features
- motion-based visual focus
- desk centerpiece
- premium novelty

### Image-specific brief
1. Hero:
   - futuristic clean tech product shot
2. Before/After:
   - plain desk vs kinetic focal point desk
3. Vibe:
   - minimal tech desk, high-end ambient light
4. Feature:
   - motion / visual focus / desk conversation piece
5. Material:
   - metallic finish, precision detail
6. Use case:
   - hand starting motion
7. SOP:
   - place / activate / enjoy
8. Dimensions:
   - footprint and safe display size
9. Brand closer:
   - universal card

---

## FL-001 蒜了鴨

### Product positioning
- Role: 引流款
- Main value: cute desk decompression object, giftable, highly memorable
- Best visual direction: cute but clean, premium playful

### Suggested text system
- Hero line: `替工作日常加一點療癒 | 蒜了鴨`
- Before/After pain: `沉悶桌面 → 更有表情的小角落`
- Vibe line: `小小一隻，剛好治癒今天`

### 3 key features
- cute emotional value
- giftable desk ornament
- easy low-threshold purchase

### Image-specific brief
1. Hero:
   - playful centered object on clean background
2. Before/After:
   - dull workspace vs lively healing corner
3. Vibe:
   - cozy bright desk lifestyle
4. Feature:
   - cute / giftable / desk mood-lifting
5. Material:
   - surface and sculpt detail
6. Use case:
   - near keyboard, notebook, coffee cup
7. SOP:
   - place / display / enjoy
8. Dimensions:
   - compact display size
9. Brand closer:
   - universal card

## Universal Prompt Fill-In Template

Use this when adding a new product:

### Product base sheet
- Product name:
- Main role:
- Main pain point:
- Main benefit:
- Three features:
- Material / finish:
- Main use case:
- Installation or usage steps:
- Dimensions:

### 9-image quick fill template
1. Hero:
   - Headline:
   - Visual cue:
2. Before/After:
   - Before:
   - After:
3. Vibe:
   - Scene style:
4. Feature:
   - Feature 1:
   - Feature 2:
   - Feature 3:
5. Material:
   - Close-up focus:
6. Use case:
   - Motion:
7. SOP:
   - Step 1:
   - Step 2:
   - Step 3:
8. Dimensions:
   - Views needed:
9. Closer:
   - Use universal store card

## Recommended Production Workflow

### For every new product
1. Make Image 1, 2, 3 first
2. Confirm product direction and style fit
3. Then make 4, 5, 6
4. Finally make 7, 8, 9

### For store consistency
- Keep Image 9 fixed for all products
- Reuse the same light-office background language
- Keep text short and premium
- Avoid marketplace-style over-decoration

## Best Next Step

For Flow Lab, the highest-return image batches are:
1. `桌下抽屜式收納盒`
2. `躺贏招財貓系列`
3. `時來運轉沙漏`

These three can define:
- organization line
- emotional healing line
- premium margin line

