const subjectsData = [
  // 1. หมวดพื้นฐานและทฤษฎีกฎหมาย
  { id: "law-fund-01", code: "LAW1001", name_th: "ความรู้พื้นฐานเกี่ยวกับกฎหมายและระบบกฎหมาย", name_en: "Introduction to Law", category: "พื้นฐาน", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "ศึกษาลักษณะของกฎหมาย บ่อเกิดและประเภทของกฎหมาย ระบบกฎหมาย ตลอดจนการปรับใช้กฎหมายเบื้องต้น" },
  { id: "law-fund-02", code: "LAW1002", name_th: "ประวัติศาสตร์กฎหมายไทยและต่างประเทศ", name_en: "Legal History", category: "พื้นฐาน", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "ศึกษาที่มาและวิวัฒนาการของระบบกฎหมายไทยและประวัติศาสตร์กฎหมายที่สำคัญของโลก" },
  { id: "law-fund-03", code: "LAW1003", name_th: "นิติปรัชญา", name_en: "Philosophy of Law", category: "พื้นฐาน", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "ศึกษาแนวความคิด หลักการ และปรัชญาเบื้องหลังของการเกิดและวัตถุประสงค์ของกฎหมาย" },
  { id: "law-fund-04", code: "LAW1004", name_th: "การใช้และการตีความกฎหมาย", name_en: "Legal Interpretation", category: "พื้นฐาน", credits: 2, universities: ["มธ.", "รามคำแหง"], description: "ศึกษาทฤษฎีและหลักเกณฑ์การตีความกฎหมายลายลักษณ์อักษร และการอุดช่องโหว่ของกฎหมาย" },
  { id: "law-fund-05", code: "LAW1005", name_th: "นิติตรรกศาสตร์และการให้เหตุผลทางกฎหมาย", name_en: "Legal Logic and Reasoning", category: "พื้นฐาน", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "ศึกษาตรรกะและเหตุผลในการนำข้อเท็จจริงมาปรับใช้กับข้อกฎหมายอย่างถูกต้อง" },
  { id: "law-fund-06", code: "LAW1006", name_th: "วิชาชีพนักกฎหมายและจรรยาบรรณ", name_en: "Legal Profession and Ethics", category: "พื้นฐาน", credits: 2, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาบทบาท หน้าที่ และจริยธรรมของวิชาชีพนักกฎหมาย เช่น ทนายความ ผู้พิพากษา อัยการ" },
  { id: "law-fund-07", code: "LAW1007", name_th: "ภาษากฎหมาย", name_en: "Legal Language", category: "พื้นฐาน", credits: 2, universities: ["มธ.", "รามคำแหง"], description: "ศึกษาการใช้ภาษาไทยและภาษาอังกฤษที่ถูกต้องสำหรับการเขียนร่างเอกสารและหนังสือทางกฎหมาย" },
  { id: "law-fund-08", code: "LAW1008", name_th: "สังคมวิทยากฎหมาย", name_en: "Sociology of Law", category: "พื้นฐาน", credits: 3, universities: ["มธ."], description: "ศึกษาความสัมพันธ์ระหว่างกฎหมายกับสังคม และผลกระทบของกฎหมายต่อพฤติกรรมมนุษย์" },
  { id: "law-fund-09", code: "LAW1009", name_th: "นิติเศรษฐศาสตร์", name_en: "Economic Analysis of Law", category: "พื้นฐาน", credits: 3, universities: ["จุฬาฯ"], description: "วิเคราะห์กฎหมายผ่านมุมมองของเศรษฐศาสตร์ เพื่อดูความคุ้มค่าและประสิทธิภาพของข้อบังคับ" },

  // 2. หมวดกฎหมายแพ่งและพาณิชย์
  { id: "law-civ-01", code: "LAW2001", name_th: "กฎหมายลักษณะบุคคล", name_en: "Persons", category: "แพ่ง", credits: 2, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "มศว.", "ม.เชียงใหม่"], description: "ศึกษาสภาพบุคคล ความสามารถของบุคคล ภูมิลำเนา สาบสูญ และนิติบุคคล" },
  { id: "law-civ-02", code: "LAW2002", name_th: "กฎหมายลักษณะนิติกรรมและสัญญา", name_en: "Juristic Acts and Contracts", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "ศึกษาหลักทั่วไปว่าด้วยนิติกรรม การแสดงเจตนา ความสมบูรณ์ของนิติกรรม และบ่อเกิดแห่งสัญญา" },
  { id: "law-civ-03", code: "LAW2003", name_th: "กฎหมายลักษณะหนี้", name_en: "Obligations", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาบ่อเกิดแห่งหนี้ ผลแห่งหนี้ ลูกหนี้และเจ้าหนี้หลายคน โอนสิทธิเรียกร้อง และความระงับแห่งหนี้" },
  { id: "law-civ-04", code: "LAW2004", name_th: "กฎหมายลักษณะละเมิด จัดการงานนอกสั่ง และลาภมิควรได้", name_en: "Delicts, Management of Affairs without Mandate, Undue Enrichment", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาความรับผิดทางประทุษร้าย การกระทำละเมิด การใช้ค่าสินไหมทดแทน" },
  { id: "law-civ-05", code: "LAW2005", name_th: "กฎหมายลักษณะทรัพย์สินและที่ดิน", name_en: "Property and Land Law", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาประเภทของทรัพย์สิน ทรัพยสิทธิ การได้มาซึ่งกรรมสิทธิ์ และสิทธิเหนือทรัพย์สิน" },
  { id: "law-civ-06", code: "LAW2006", name_th: "กฎหมายลักษณะเอกเทศสัญญา 1", name_en: "Specific Contracts I", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาลักษณะสัญญา ซื้อขาย แลกเปลี่ยน ให้ เช่าทรัพย์ เช่าซื้อ" },
  { id: "law-civ-07", code: "LAW2007", name_th: "กฎหมายลักษณะเอกเทศสัญญา 2", name_en: "Specific Contracts II", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาลักษณะสัญญา ยืม ฝากทรัพย์ เก็บของในคลังสินค้า ตัวแทน นายหน้า" },
  { id: "law-civ-08", code: "LAW2008", name_th: "กฎหมายลักษณะเอกเทศสัญญา 3", name_en: "Specific Contracts III", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาลักษณะสัญญา ประกันภัย รับขน ค้ำประกัน จำนอง จำนำ" },
  { id: "law-civ-09", code: "LAW2009", name_th: "กฎหมายลักษณะตั๋วเงินและบัญชีเดินสะพัด", name_en: "Negotiable Instruments", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาหลักพานิชย์ตั๋วแลกเงิน ตั๋วสัญญาใช้เงิน และเช็ค" },
  { id: "law-civ-10", code: "LAW2010", name_th: "กฎหมายลักษณะหุ้นส่วนและบริษัท", name_en: "Business Organizations", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาการจัดตั้ง การดำเนินธุรกิจ และการเลิกห้างหุ้นส่วนและบริษัทจำกัด" },
  { id: "law-civ-11", code: "LAW2011", name_th: "กฎหมายลักษณะครอบครัว", name_en: "Family Law", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาการหมั้น การสมรส ความสัมพันธ์ระหว่างสามีภรรยา บิดามารดากับบุตร" },
  { id: "law-civ-12", code: "LAW2012", name_th: "กฎหมายลักษณะมรดก", name_en: "Succession Law", category: "แพ่ง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศึกษาการตกทอดแห่งทรัพย์มรดก สิทธิในการรับมรดก และการทำพินัยกรรม" },
  { id: "law-civ-13", code: "LAW2013", name_th: "หลักเกณฑ์การทำสัญญาและเอกสารทางกฎหมาย", name_en: "Legal Document Preparation", category: "แพ่ง", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "ทักษะและการร่างสัญญาทางธุรกิจ และเอกสารทางกฎหมายที่สำคัญ" },

  // 3. หมวดกฎหมายอาญาและนิติวิทยาศาสตร์
  { id: "law-crim-01", code: "LAW3001", name_th: "กฎหมายอาญา ภาคทั่วไป", name_en: "Criminal Law: General Principles", category: "อาญา", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "ศึกษาหลักความรับผิดทางอาญา โครงสร้างความผิด เหตุยกเว้นความผิดและเหตุยกเว้นโทษ" },
  { id: "law-crim-02", code: "LAW3002", name_th: "กฎหมายอาญา ภาคความผิด", name_en: "Criminal Law: Specific Offenses", category: "อาญา", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "ศึกษาความผิดต่อความมั่นคง ชีวิตและร่างกาย และทรัพย์" },
  { id: "law-crim-03", code: "LAW3003", name_th: "กฎหมายอาญา ภาคลหุโทษ", name_en: "Petty Offenses", category: "อาญา", credits: 2, universities: ["มธ.", "รามคำแหง"], description: "ศึกษาลักษณะความผิดเล็กน้อยที่มีระวางโทษสถานเบา" },
  { id: "law-crim-04", code: "LAW3004", name_th: "กฎหมายเกี่ยวกับกระบวนการยุติธรรมเด็กและเยาวชน", name_en: "Juvenile Justice Law", category: "อาญา", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศาลเยาวชนและครอบครัว การคุ้มครองสวัสดิภาพเด็ก" },
  { id: "law-crim-05", code: "LAW3005", name_th: "อาชญาวิทยาและทัณฑวิทยา", name_en: "Criminology and Penology", category: "อาญา", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "วิเคราะห์สาเหตุของการเกิดอาชญากรรม ตลอดจนการลงโทษและการแก้ไขฟื้นฟู" },
  { id: "law-crim-06", code: "LAW3006", name_th: "นิติวิทยาศาสตร์และนิติเวชศาสตร์", name_en: "Forensic Science and Medicine", category: "อาญา", credits: 3, universities: ["มธ.", "จุฬาฯ"], description: "การพิสูจน์หลักฐานทางวิทยาศาสตร์และการแพทย์เพื่อใช้ในคดีอาญา" },
  { id: "law-crim-07", code: "LAW3007", name_th: "กฎหมายเกี่ยวกับยาเสพติด", name_en: "Narcotics Law", category: "อาญา", credits: 2, universities: ["รามคำแหง"], description: "ความผิดและกระบวนการพิจารณาคดีความผิดเกี่ยวกับยาเสพติดให้โทษ" },

  // 4. หมวดกฎหมายมหาชนและการปกครอง
  { id: "law-pub-01", code: "LAW4001", name_th: "หลักกฎหมายมหาชนเบื้องต้น", name_en: "Principles of Public Law", category: "มหาชน", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ความหมายและวิวัฒนาการของกฎหมายมหาชน สถานะของรัฐ หลักนิติรัฐ" },
  { id: "law-pub-02", code: "LAW4002", name_th: "กฎหมายรัฐธรรมนูญและสถาบันการเมือง", name_en: "Constitutional Law", category: "มหาชน", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "โครงสร้างองค์กรรัฐ สิทธิ เสรีภาพ การใช้อำนาจอธิปไตย" },
  { id: "law-pub-03", code: "LAW4003", name_th: "กฎหมายปกครอง", name_en: "Administrative Law", category: "มหาชน", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "บริหารราชการแผ่นดิน นิติกรรมทางปกครอง และสัญญาทางปกครอง" },
  { id: "law-pub-04", code: "LAW4004", name_th: "วิธีพิจารณาคดีปกครอง", name_en: "Administrative Procedure", category: "มหาชน", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ศาลปกครองและวิธีพิจารณาตัดสินคดีพิพาทระหว่างรัฐกับเอกชน" },
  { id: "law-pub-05", code: "LAW4005", name_th: "กฎหมายการคลังและภาษีอากร", name_en: "Public Finance and Taxation", category: "มหาชน", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "ระบบภาษีเงินได้ ภาษีมูลค่าเพิ่ม และกฎหมายว่าด้วยการเงินการคลังของรัฐ" },
  { id: "law-pub-06", code: "LAW4006", name_th: "กฎหมายเกี่ยวกับการเลือกตั้ง", name_en: "Election Law", category: "มหาชน", credits: 2, universities: ["มธ."], description: "กฎหมายประกอบรัฐธรรมนูญว่าด้วยพรรคการเมืองและการเลือกตั้ง" },
  { id: "law-pub-07", code: "LAW4007", name_th: "กฎหมายปกครองส่วนท้องถิ่น", name_en: "Local Administrative Law", category: "มหาชน", credits: 3, universities: ["มธ.", "รามคำแหง"], description: "องค์กรปกครองส่วนท้องถิ่น อำนาจหน้าที่ และความสัมพันธ์กับส่วนกลาง" },
  { id: "law-pub-08", code: "LAW4008", name_th: "กฎหมายการผังเมืองและอาคาร", name_en: "Urban Planning Law", category: "มหาชน", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "กฎหมายควบคุมอาคาร ผังเมือง และการเวนคืนอสังหาริมทรัพย์" },

  // 5. หมวดกฎหมายวิธีพิจารณาความและพยาน
  { id: "law-proc-01", code: "LAW5001", name_th: "พระธรรมนูญศาลยุติธรรม", name_en: "Law on the Organization of Courts", category: "วิธีพิจารณา", credits: 2, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "การจัดตั้งและอำนาจพิจารณาพิพากษาคดีของศาลยุติธรรม" },
  { id: "law-proc-02", code: "LAW5002", name_th: "กฎหมายวิธีพิจารณาความแพ่ง", name_en: "Civil Procedure Law", category: "วิธีพิจารณา", credits: 4, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "กระบวนการดำเนินคดีแพ่ง คู่ความ คำฟ้อง การพิจารณาและพิพากษา" },
  { id: "law-proc-03", code: "LAW5003", name_th: "กฎหมายวิธีพิจารณาความอาญา", name_en: "Criminal Procedure Law", category: "วิธีพิจารณา", credits: 4, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "อำนาจสอบสวน การจับ ควบคุม ฟ้องคดี และการพิจารณาคดีอาญา" },
  { id: "law-proc-04", code: "LAW5004", name_th: "กฎหมายลักษณะพยานหลักฐาน", name_en: "Law of Evidence", category: "วิธีพิจารณา", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "หลักเกณฑ์การรับฟังพยานหลักฐานในคดีแพ่งและคดีอาญา" },
  { id: "law-proc-05", code: "LAW5005", name_th: "กฎหมายล้มละลายและการฟื้นฟูกิจการ", name_en: "Bankruptcy and Rehabilitation", category: "วิธีพิจารณา", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "กระบวนการพิจารณาคดีล้มละลาย การพิทักษ์ทรัพย์ และการประนอมหนี้" },
  { id: "law-proc-06", code: "LAW5006", name_th: "การว่าความและศาลจำลอง", name_en: "Advocacy and Moot Court", category: "วิธีพิจารณา", credits: 2, universities: ["มธ.", "จุฬาฯ", "ม.เชียงใหม่"], description: "ฝึกปฏิบัติดำเนินคดีและจำลองสถานการณ์ในชั้นพิจารณา" },
  { id: "law-proc-07", code: "LAW5007", name_th: "การระงับข้อพิพาททางเลือก", name_en: "Alternative Dispute Resolution", category: "วิธีพิจารณา", credits: 2, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "การอนุญาโตตุลาการ การไกล่เกลี่ย และการประนอมข้อพิพาท" },
  { id: "law-proc-08", code: "LAW5008", name_th: "การบังคับคดีแพ่งและอาญา", name_en: "Legal Execution", category: "วิธีพิจารณา", credits: 2, universities: ["มธ.", "รามคำแหง"], description: "กระบวนการยึด อายัด และขายทอดตลาดทรัพย์สิน" },

  // 6. หมวดกฎหมายระหว่างประเทศ
  { id: "law-inter-01", code: "LAW6001", name_th: "กฎหมายระหว่างประเทศแผนกคดีเมือง", name_en: "Public International Law", category: "ระหว่างประเทศ", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "ความสัมพันธ์ระดับรัฐ สนธิสัญญา เอกสิทธิ์ ความคุ้มกันของรัฐ" },
  { id: "law-inter-02", code: "LAW6002", name_th: "กฎหมายระหว่างประเทศแผนกคดีบุคคลและคดีอาญา", name_en: "Private International Law", category: "ระหว่างประเทศ", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "การขัดกันแห่งกฎหมาย การรับรองคำพิพากษาต่างประเทศ" },
  { id: "law-inter-03", code: "LAW6003", name_th: "กฎหมายองค์การระหว่างประเทศ", name_en: "International Organizations", category: "ระหว่างประเทศ", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "สหประชาชาติ และองค์กรระหว่างประเทศที่สำคัญทั้วโลก" },
  { id: "law-inter-04", code: "LAW6004", name_th: "กฎหมายว่าด้วยทะเล", name_en: "Law of the Sea", category: "ระหว่างประเทศ", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "น่านน้ำ เขตเศรษฐกิจจำเพาะ และข้อพิพาททางทะเล" },
  { id: "law-inter-05", code: "LAW6005", name_th: "กฎหมายอาเซียน", name_en: "ASEAN Law", category: "ระหว่างประเทศ", credits: 2, universities: ["มธ.", "รามคำแหง", "ม.เชียงใหม่"], description: "กฎบัตรอาเซียน และข้อตกลงประชาคมเศรษฐกิจอาเซียน" },
  { id: "law-inter-06", code: "LAW6006", name_th: "กฎหมายการค้าระหว่างประเทศ", name_en: "International Trade Law", category: "ระหว่างประเทศ", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "การค้าระหว่างประเทศ การขนส่ง INCOTERMS และการเปิด L/C" },
  { id: "law-inter-07", code: "LAW6007", name_th: "กฎหมายสิทธิมนุษยชน", name_en: "Human Rights Law", category: "ระหว่างประเทศ", credits: 3, universities: ["มธ.", "รามคำแหง"], description: "สิทธิมนุษยชนตามกฎหมายระหว่างประเทศและในประเทศ" },

  // 7. หมวดกฎหมายเฉพาะทางและสมัยใหม่
  { id: "law-spec-01", code: "LAW7001", name_th: "กฎหมายแรงงานและการประกันสังคม", name_en: "Labour and Social Security Law", category: "เฉพาะทาง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "ม.เชียงใหม่"], description: "สัญญาจ้างแรงงาน กฎหมายคุ้มครองแรงงาน แรงงานสัมพันธ์" },
  { id: "law-spec-02", code: "LAW7002", name_th: "กฎหมายทรัพย์สินทางปัญญา", name_en: "Intellectual Property Law", category: "เฉพาะทาง", credits: 3, universities: ["มธ.", "จุฬาฯ", "รามคำแหง", "มศว."], description: "ลิขสิทธิ์ สิทธิบัตร เครื่องหมายการค้า" },
  { id: "law-spec-03", code: "LAW7003", name_th: "กฎหมายเศรษฐกิจและการค้าระหว่างประเทศ", name_en: "Economic Law", category: "เฉพาะทาง", credits: 3, universities: ["มธ.", "จุฬาฯ"], description: "นโยบายการค้าและการแข่งขันทางการค้า" },
  { id: "law-spec-04", code: "LAW7004", name_th: "กฎหมายการธนาคารและสถาบันการเงิน", name_en: "Banking and Financial Institutions Law", category: "เฉพาะทาง", credits: 3, universities: ["มธ.", "จุฬาฯ"], description: "ธุรกิจธนาคาร หลักทรัพย์ ตลาดหลักทรัพย์" },
  { id: "law-spec-05", code: "LAW7005", name_th: "กฎหมายคุ้มครองผู้บริโภค", name_en: "Consumer Protection Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ.", "รามคำแหง"], description: "การคุ้มครองสัญญา โฆษณา สินค้าอันตราย" },
  { id: "law-spec-06", code: "LAW7006", name_th: "กฎหมายสิ่งแวดล้อม", name_en: "Environmental Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ.", "จุฬาฯ", "รามคำแหง"], description: "การจัดการทรัพยากรธรรมชาติและคุณภาพสิ่งแวดล้อม" },
  { id: "law-spec-07", code: "LAW7007", name_th: "กฎหมายเทคโนโลยีสารสนเทศ / กฎหมายไซเบอร์", name_en: "IT / Cyber Law", category: "เฉพาะทาง", credits: 3, universities: ["มธ.", "จุฬาฯ", "ม.เชียงใหม่"], description: "พ.ร.บ.ว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ อาชญากรรมไซเบอร์" },
  { id: "law-spec-08", code: "LAW7008", name_th: "กฎหมายคุ้มครองข้อมูลส่วนบุคคล", name_en: "Privacy / PDPA Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล (PDPA)" },
  { id: "law-spec-09", code: "LAW7009", name_th: "กฎหมายพลังงาน", name_en: "Energy Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "การปิโตรเลียม กฟผ. และพลังงานทดแทน" },
  { id: "law-spec-10", code: "LAW7010", name_th: "กฎหมายการแพทย์และสาธารณสุข", name_en: "Medical Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ."], description: "ความรับผิดของแพทย์ สถานพยาบาล กฎหมายที่เกี่ยวกับยา" },
  { id: "law-spec-11", code: "LAW7011", name_th: "กฎหมายบันเทิงและกีฬา", name_en: "Entertainment and Sports Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ."], description: "สัญญาศิลปิน ค่ายเพลง และสัญญาการกีฬา" },
  { id: "law-spec-12", code: "LAW7012", name_th: "กฎหมายเกี่ยวกับการขนส่ง", name_en: "Transport Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ."], description: "การรับขนของทางเส้นทางบก น้ำ อากาศ" },
  { id: "law-spec-13", code: "LAW7013", name_th: "กฎหมายเกี่ยวกับอสังหาริมทรัพย์", name_en: "Real Estate Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ.", "จุฬาฯ"], description: "อาคารชุด หมู่บ้านจัดสรร ภาษีที่ดิน" },
  { id: "law-spec-14", code: "LAW7014", name_th: "กฎหมายว่าด้วยการลงทุน", name_en: "Investment Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ."], description: "BOI สิทธิประโยชน์ในการลงทุน" },
  { id: "law-spec-15", code: "LAW7015", name_th: "กฎหมายเกษตรและอุตสาหกรรมเกษตร", name_en: "Agrarian Law", category: "เฉพาะทาง", credits: 2, universities: ["มธ."], description: "การปฏิรูปที่ดิน สัญญาเกษตรพันธสัญญา" },
  { id: "law-spec-16", code: "LAW7016", name_th: "กฎหมายทหาร", name_en: "Military Law", category: "เฉพาะทาง", credits: 2, universities: ["รามคำแหง"], description: "ศาลทหาร ธรรมนูญศาลทหาร การรับราชการทหาร" },
];

const categories = [
  { id: "cat-1", name: "พื้นฐาน", icon: "📚" },
  { id: "cat-2", name: "แพ่ง", icon: "🤝" },
  { id: "cat-3", name: "อาญา", icon: "⚖️" },
  { id: "cat-4", name: "มหาชน", icon: "🏛️" },
  { id: "cat-5", name: "วิธีพิจารณา", icon: "📝" },
  { id: "cat-6", name: "ระหว่างประเทศ", icon: "🌍" },
  { id: "cat-7", name: "เฉพาะทาง", icon: "💡" }
];

const universities = [
  { id: "uni-1", name: "มธ." },
  { id: "uni-2", name: "จุฬาฯ" },
  { id: "uni-3", name: "รามคำแหง" },
  { id: "uni-4", name: "มศว." },
  { id: "uni-5", name: "ม.เชียงใหม่" }
];
